# models.py in your app
from django.db import models

class Email(models.Model):
    sender = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    attachments = models.FileField(upload_to='attachments/', blank=True, null=True)
    source = models.CharField(max_length=50, default='unknown')
    def __str__(self):
        return self.subject
    def filename(self):
        return os.path.basename(self.attachments.name)