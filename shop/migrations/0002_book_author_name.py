# Generated by Django 3.1.3 on 2020-11-30 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='author_name',
            field=models.CharField(default='author', max_length=255),
            preserve_default=False,
        ),
    ]