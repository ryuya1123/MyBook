# Generated by Django 2.2.18 on 2021-02-11 01:48

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_book'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.book_image_file_path),
        ),
    ]
