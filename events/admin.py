from django.contrib import admin
from .models import Event, Registration, DeletedEvent

class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = ('user', 'registered_at')
    fields = ('user', 'registered_at', 'attended')

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

class SchoolYearInputFilter(InputFilter):
    title = '學年度'
    parameter_name = 'school_year'
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(school_year=self.value())
        return queryset

class YearInputFilter(InputFilter):
    title = '年度'
    parameter_name = 'year'
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(year=self.value())
        return queryset

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    exclude = ('is_deleted',)
    readonly_fields = ('registered_count',)
    list_display = ('title', 'school_year', 'year', 'semester', 'date', 'capacity', 'registered_count')
    list_filter = (SchoolYearInputFilter, YearInputFilter, 'semester')
    search_fields = ('title',)
    inlines = [RegistrationInline]
    actions = ['soft_delete']

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
    list_display = ('event', 'user', 'registered_at', 'attended')
    list_filter = ('event', 'attended')
    list_editable = ('attended',)
    search_fields = ('user__username', 'event__title')
