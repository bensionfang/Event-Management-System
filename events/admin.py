from django.contrib import admin
from .models import Event, Registration, DeletedEvent

class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = ('name', 'email', 'check_in_id', 'registered_at')
    fields = ('name', 'email', 'check_in_id', 'registered_at', 'attended')

from django.contrib.admin import SimpleListFilter

class InputFilter(SimpleListFilter):
    template = 'admin/input_filter.html'
    def lookups(self, request, model_admin):
        return ((),)
    def choices(self, changelist):
        all_choice = {
            'query_parts': ((k, v) for k, v in changelist.get_filters_params().items() if k != self.parameter_name),
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
        }
        yield all_choice

class SchoolYearFilter(admin.SimpleListFilter):
    title = '學年度'
    parameter_name = 'school_year'
    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.order_by('-school_year').values_list('school_year', flat=True).distinct()
        return [(str(y), str(y)) for y in qs if y]
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(school_year=self.value())
        return queryset

class YearFilter(admin.SimpleListFilter):
    title = '年度'
    parameter_name = 'year'
    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.order_by('-year').values_list('year', flat=True).distinct()
        return [(str(y), str(y)) for y in qs if y]
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(year=self.value())
        return queryset

class SemesterFilter(admin.SimpleListFilter):
    title = '學期'
    parameter_name = 'semester'
    def lookups(self, request, model_admin):
        from .models import Event
        return Event.SEMESTER_CHOICES
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(semester=self.value())
        return queryset

class TargetAudienceFilter(admin.SimpleListFilter):
    title = '參加對象'
    parameter_name = 'target_audience'
    def lookups(self, request, model_admin):
        from .models import Event
        return Event.TARGET_AUDIENCE_CHOICES
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(target_audience=self.value())
        return queryset

class CurrentStatusFilter(admin.SimpleListFilter):
    title = '目前狀態'
    parameter_name = 'status'
    def lookups(self, request, model_admin):
        return (
            ('full', '已額滿'),
            ('upcoming', '即將開放'),
            ('open', '報名中'),
            ('closed', '已結束'),
        )
    def queryset(self, request, queryset):
        from django.utils import timezone
        from django.db.models import F
        now = timezone.now()
        val = self.value()
        if val == 'full':
            return queryset.filter(registered_count__gte=F('capacity'))
        elif val == 'upcoming':
            return queryset.filter(registration_start_time__gt=now, registered_count__lt=F('capacity'))
        elif val == 'closed':
            return queryset.filter(registration_end_time__lt=now, registered_count__lt=F('capacity'))
        elif val == 'open':
            return queryset.filter(registration_start_time__lte=now, registration_end_time__gte=now, registered_count__lt=F('capacity'))
        return queryset

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    exclude = ('is_deleted',)
    readonly_fields = ('registered_count',)
    list_display = ('title', 'status_tag', 'school_year', 'year', 'semester', 'target_audience', 'date', 'capacity', 'registered_count')
    list_filter = (CurrentStatusFilter, SchoolYearFilter, YearFilter, SemesterFilter, TargetAudienceFilter)
    
    def status_tag(self, obj):
        from django.utils.safestring import mark_safe
        from django.utils import timezone
        now = timezone.now()
        if obj.registered_count >= obj.capacity:
            return mark_safe('<span style="background-color: #d9534f; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.85em; font-weight: bold; white-space: nowrap;">已額滿</span>')
        
        if obj.registration_start_time and obj.registration_end_time:
            if now < obj.registration_start_time:
                return mark_safe('<span style="background-color: #f0ad4e; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.85em; font-weight: bold; white-space: nowrap;">即將開放</span>')
            elif now > obj.registration_end_time:
                return mark_safe('<span style="background-color: #777777; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.85em; font-weight: bold; white-space: nowrap;">已結束</span>')
        
        return mark_safe('<span style="background-color: #5cb85c; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.85em; font-weight: bold; white-space: nowrap;">報名中</span>')
    status_tag.short_description = '目前狀態'
    
    search_fields = ('title', 'location', 'organizer')
    search_form_template = 'admin/events_search_form.html'
    inlines = [RegistrationInline]
    actions = ['soft_delete']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_search_fields(self, request):
        search_field = request.GET.get('search_field')
        if search_field == 'title':
            return ('title',)
        elif search_field == 'location':
            return ('location',)
        elif search_field == 'organizer':
            return ('organizer',)
        return super().get_search_fields(request)

    from django.db import models
    from django import forms
    formfield_overrides = {
        models.DateTimeField: {
            'widget': forms.SplitDateTimeWidget(
                date_attrs={'type': 'date', 'style': 'padding: 6px;'},
                time_attrs={'type': 'time', 'style': 'padding: 6px; margin-left: 5px;'}
            )
        },
    }

    class Media:
        css = {
            'all': ('css/admin_custom.css?v=2',)
        }

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_deleted=False)

    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)
    soft_delete.short_description = "將選取的活動移至資源回收桶"

    def delete_model(self, request, obj):
        obj.is_deleted = True
        obj.save()

    def delete_queryset(self, request, queryset):
        queryset.update(is_deleted=True)

@admin.register(DeletedEvent)
class DeletedEventAdmin(admin.ModelAdmin):
    exclude = ('is_deleted',)
    readonly_fields = ('title', 'school_year', 'year', 'semester', 'date', 'capacity', 'registered_count', 'description')
    list_display = ('title', 'school_year', 'year', 'semester', 'date', 'capacity', 'registered_count')
    search_fields = ('title',)
    actions = ['restore', 'hard_delete']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_deleted=True)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def restore(self, request, queryset):
        queryset.update(is_deleted=False)
    restore.short_description = "從資源回收桶還原選取的活動"
    
    def hard_delete(self, request, queryset):
        # 真正從資料庫刪除
        for obj in queryset:
            obj.delete()
    hard_delete.short_description = "永久刪除選取的活動 (無法還原)"

    # Disable adding new deleted events manually
    def has_add_permission(self, request):
        return False

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'name', 'email', 'registered_at', 'attended', 'check_in_id')
    list_filter = ('event', 'attended')
    list_editable = ('attended',)
    search_fields = ('name', 'email', 'event__title')
    actions = ['export_as_csv', 'mark_as_attended', 'mark_as_absent']

    def mark_as_attended(self, request, queryset):
        updated = queryset.update(attended=True)
        self.message_user(request, f"成功將 {updated} 位報名者標記為「已出席」。")
    mark_as_attended.short_description = "✔ 將選取的人員標記為「已出席」"

    def mark_as_absent(self, request, queryset):
        updated = queryset.update(attended=False)
        self.message_user(request, f"成功將 {updated} 位報名者標記為「未出席」。")
    mark_as_absent.short_description = "✖ 將選取的人員標記為「未出席」"

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from django.utils import timezone
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="registration_list.csv"'
        response.write('\ufeff')  # 寫入 BOM，讓 Excel 正常顯示中文
        
        writer = csv.writer(response)
        writer.writerow(['活動名稱', '姓名', 'Email', '報名時間', '出席狀態', '報到代碼'])
        
        for obj in queryset:
            writer.writerow([
                obj.event.title,
                obj.name,
                obj.email,
                timezone.localtime(obj.registered_at).strftime('%Y-%m-%d %H:%M') if obj.registered_at else '',
                '已出席' if obj.attended else '未出席',
                obj.check_in_id,
            ])
            
        return response
    export_as_csv.short_description = "📥 匯出選取的報名名單 (CSV 檔)"
