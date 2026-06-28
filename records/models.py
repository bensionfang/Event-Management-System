from django.db import models
from events.models import Event

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Record(models.Model):
    SEMESTER_CHOICES = [
        (1, '上學期'),
        (2, '下學期'),
    ]
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='record', verbose_name="對應活動")
    school_year = models.PositiveIntegerField(verbose_name="學年度", help_text="例如：113")
    year = models.PositiveIntegerField(verbose_name="年度", help_text="例如：2026", default=2026)
    semester = models.IntegerField(choices=SEMESTER_CHOICES, verbose_name="學期")
    
    summary = models.TextField(verbose_name="活動成果摘要")
    cover_image = models.ImageField(upload_to='records/images/', verbose_name="活動首圖/照片", blank=True, null=True)
    attachment = models.FileField(upload_to='records/attachments/', verbose_name="附件檔案", blank=True, null=True)
    
    is_public = models.BooleanField(default=True, verbose_name="是否公開展示")
    is_deleted = models.BooleanField(default=False, verbose_name="是否已刪除")

    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        verbose_name = "歷年紀錄"
        verbose_name_plural = "歷年紀錄"

    def __str__(self):
        return f"{self.school_year}-{self.get_semester_display()} {self.event.title}"
