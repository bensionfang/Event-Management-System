from django.db import models
from django.conf import settings

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
    school_year = models.PositiveIntegerField(verbose_name="學年度", help_text="例如：113", default=113)
    year = models.PositiveIntegerField(verbose_name="年度", help_text="例如：2026", default=2026)
    semester = models.IntegerField(choices=SEMESTER_CHOICES, verbose_name="學期", default=1)
    date = models.DateTimeField(verbose_name="活動時間")
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

class DeletedEvent(Event):
    class Meta:
        proxy = True
        verbose_name = "資源回收桶 (已刪除活動)"
        verbose_name_plural = "資源回收桶 (已刪除活動)"

class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations', verbose_name="活動")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations', verbose_name="報名者")
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name="報名時間")
    attended = models.BooleanField(default=False, verbose_name="是否出席")
    
    class Meta:
        verbose_name = "報名紀錄"
        verbose_name_plural = "報名紀錄"
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user} - {self.event.title}"
