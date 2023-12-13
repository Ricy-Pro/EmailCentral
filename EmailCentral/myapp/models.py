# models.py
from django.utils import timezone
from django.db import models

class Attachment(models.Model):
    name = models.CharField(max_length=255)
    content = models.BinaryField()

    def __str__(self):
        return self.name

class Email(models.Model):
    sender = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    attachments = models.ManyToManyField(Attachment, blank=True)
    source = models.CharField(max_length=50, default='unknown')
    received_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)  # Set a default value

    def __str__(self):
        return self.subject
