# Generated by Django 4.2.11 on 2024-07-29 13:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0078_alter_assessment_high_inflection_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="assessment",
            name="skip_high_result_page",
            field=models.ForeignKey(
                blank=True,
                help_text="The page to show a user if they skip a question",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assessment_high_skip",
                to="home.contentpage",
            ),
        ),
        migrations.AddField(
            model_name="assessment",
            name="skip_threshold",
            field=models.FloatField(
                default=0,
                help_text="If a user skips equal to or greater than this many questions they will be presented with the skip page",
            ),
        ),
    ]