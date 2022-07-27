# Generated by Django 3.2.7 on 2021-10-06 05:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0062_comment_models_and_pagesubscription'),
        ('home', '0008_alter_contentpage_whatsapp_body'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentPageIndex',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='include_in_footer',
            field=models.BooleanField(default=False),
        ),
    ]
