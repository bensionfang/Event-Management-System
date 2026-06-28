from django.db import models
from django.conf import settings
import uuid

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Event(models.Model):
    SEMESTER_CHOICES = [
        (1, '上學期'),
        (2, '下學期'),
    ]
    title = models.CharField(max_length=200, verbose_name="活動名稱")
    description = models.TextField(verbose_name="活動描述")
    school_year = models.PositiveIntegerField(verbose_name="學年度", default=113)
    year = models.PositiveIntegerField(verbose_name="年度", default=2026)
    semester = models.IntegerField(choices=SEMESTER_CHOICES, verbose_name="學期", default=1)
    date = models.DateTimeField(verbose_name="活動開始時間")
    end_time = models.DateTimeField(verbose_name="活動結束時間", null=True)
    location = models.CharField(max_length=200, verbose_name="地點", default="")
    organizer = models.CharField(max_length=200, verbose_name="主辦單位", blank=True, default="")
    TARGET_AUDIENCE_CHOICES = [
        ('不限', '不限'),
        ('教職員', '教職員'),
        ('學生', '學生'),
    ]
    target_audience = models.CharField(max_length=200, choices=TARGET_AUDIENCE_CHOICES, verbose_name="參加對象", default="不限")
    registration_start_time = models.DateTimeField(verbose_name="報名開始時間", null=True)
    registration_end_time = models.DateTimeField(verbose_name="報名結束時間", null=True)
    capacity = models.PositiveIntegerField(verbose_name="名額上限")
    registered_count = models.PositiveIntegerField(default=0, verbose_name="已報名人數")
    
    # Soft delete flag
    is_deleted = models.BooleanField(default=False, verbose_name="是否已刪除")
    
    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        verbose_name = "活動"
        verbose_name_plural = "活動"

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        
        if self.date and self.end_time and self.date > self.end_time:
            raise ValidationError({'end_time': "活動結束時間不能早於活動開始時間。"})
            
        if self.registration_start_time and self.registration_end_time and self.registration_start_time > self.registration_end_time:
            raise ValidationError({'registration_end_time': "報名結束時間不能早於報名開始時間。"})

class DeletedEvent(Event):
    class Meta:
        proxy = True
        verbose_name = "資源回收桶 (已刪除活動)"
        verbose_name_plural = "資源回收桶 (已刪除活動)"

class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations', verbose_name="活動")
    name = models.CharField(max_length=100, verbose_name="姓名")
    email = models.EmailField(verbose_name="聯絡信箱")
    check_in_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="簽到專屬ID")
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name="報名時間")
    attended = models.BooleanField(default=False, verbose_name="是否出席")
    
    class Meta:
        verbose_name = "報名紀錄"
        verbose_name_plural = "報名紀錄"
        unique_together = ('event', 'email')

    def __str__(self):
        return f"{self.name} - {self.event.title}"
