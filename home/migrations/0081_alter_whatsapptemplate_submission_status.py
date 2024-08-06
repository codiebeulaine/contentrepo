# Generated by Django 4.2.11 on 2024-08-06 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0080_assessment_skip_high_result_page_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="whatsapptemplate",
            name="submission_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("NOT_SUBMITTED_YET", "Not Submitted Yet"),
                    ("SUBMITTED", "Submitted"),
                    ("FAILED", "Failed"),
                ],
                default="",
                max_length=30,
            ),
        ),
    ]