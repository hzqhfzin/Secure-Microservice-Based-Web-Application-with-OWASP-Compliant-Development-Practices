from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('normal', 'Normal User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='normal')

    def __str__(self):
        return f"{self.username} ({self.role})"

class InventoryItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    item_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    status = models.CharField(max_length=50, default='Available')
    uploaded_file = models.FileField(upload_to='uploads/', blank=True, null=True)

    def __str__(self):
        return self.item_name