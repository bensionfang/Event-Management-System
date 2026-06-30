from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Record

class RecordAdminForm(forms.ModelForm):
    class Meta:
        model = Record
        exclude = ('is_deleted',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'event' in self.fields:
            from events.models import Event
            self.fields['event'].queryset = Event.objects.filter(is_deleted=False)

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            if attachment.size > 5 * 1024 * 1024:
                raise ValidationError("檔案大小不能超過 5MB")
        return attachment

    def clean_cover_image(self):
        cover_image = self.cleaned_data.get('cover_image')
        if cover_image:
            if cover_image.size > 5 * 1024 * 1024:
                raise ValidationError("照片大小不能超過 5MB")
        return cover_image

from django.contrib.admin import SimpleListFilter

class SoftDeleteFilter(SimpleListFilter):
    title = '資源回收桶'
    parameter_name = 'is_deleted'

    def lookups(self, request, model_admin):
        return (
            ('1', '已刪除'),
        )

    def choices(self, changelist):
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string({}, [self.parameter_name]),
            'display': '全部',
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == str(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_deleted=True)
        if self.value() is None:
            return queryset.filter(is_deleted=False)
        return queryset

class InputFilter(SimpleListFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        return ((),)

    def choices(self, changelist):
        # We need to provide the query string to clear the filter
        all_choice = {
            'query_parts': (
                (k, v)
                for k, v in changelist.get_filters_params().items()
                if k != self.parameter_name
            ),
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

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    form = RecordAdminForm
    list_display = ('event', 'school_year', 'year', 'semester', 'is_public')
    list_filter = (SchoolYearInputFilter, YearInputFilter, 'semester', 'is_public')
    list_editable = ('is_public',)
    
    class Media:
        js = ('admin/js/record_auto_fill.js',)
