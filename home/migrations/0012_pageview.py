# Generated by Django 3.2.7 on 2021-12-14 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0062_comment_models_and_pagesubscription'),
        ('home', '0011_add_index_api_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('data', models.JSONField(blank=True, default=dict, null=True)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='home.contentpage')),
                ('revision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='wagtailcore.pagerevision')),
            ],
        ),
    ]
