from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # 校內身分欄位
    student_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="學號/教職員編號")
    is_school_member = models.BooleanField(default=False, verbose_name="是否為校內人員")
    
    # 校外身分則使用原本的 email/username
    
    class Meta:
        verbose_name = "使用者"
        verbose_name_plural = "使用者"

    def __str__(self):
        return self.username
