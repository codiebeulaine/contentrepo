# Generated by Django 4.0.6 on 2022-08-10 07:24

import wagtail.blocks
import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0018_pageview_platform'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpage',
            name='related_pages',
            field=wagtail.fields.StreamField([('related_page', wagtail.blocks.PageChooserBlock())], blank=True, null=True, use_json_field=True),
        ),
    ]
