# Generated by Django 4.2.11 on 2024-03-25 08:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0051_customdocument"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customdocument",
            name="source",
        ),
        migrations.AlterField(
            model_name="customdocument",
            name="file",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=[
                            "doc",
                            "docx",
                            "xls",
                            "xlsx",
                            "ppt",
                            "pptx",
                            "pdf",
                            "txt",
                        ]
                    )
                ],
            ),
        ),
    ]
