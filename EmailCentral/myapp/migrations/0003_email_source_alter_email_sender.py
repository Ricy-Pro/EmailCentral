# Generated by Django 5.0 on 2023-12-12 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_email_delete_todoitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='source',
            field=models.CharField(default='unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='email',
            name='sender',
            field=models.CharField(max_length=255),
        ),
    ]