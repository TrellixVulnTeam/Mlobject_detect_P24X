# Generated by Django 4.0 on 2021-12-14 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dj_object_detection', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.URLField(null=True),
        ),
    ]
