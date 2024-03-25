# Generated by Django 4.2.11 on 2024-03-19 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0060_delete_templateexamplevalue"),
    ]

    operations = [
        migrations.CreateModel(
            name="TemplateExampleValue",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(blank=True, default="Test", max_length=512)),
            ],
            options={
                "verbose_name": "Example Value",
                "verbose_name_plural": "Example Value",
            },
        ),
        migrations.AddField(
            model_name="whatsapptemplate",
            name="example_values",
            field=models.ManyToManyField(to="home.templateexamplevalue"),
        ),
    ]
