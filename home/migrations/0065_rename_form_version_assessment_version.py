# Generated by Django 4.2.11 on 2024-06-10 18:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0064_rename_version_assessment_form_version"),
    ]

    operations = [
        migrations.RenameField(
            model_name="assessment",
            old_name="form_version",
            new_name="version",
        ),
    ]
