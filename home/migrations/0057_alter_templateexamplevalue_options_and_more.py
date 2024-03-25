# Generated by Django 4.2.11 on 2024-03-19 11:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0056_alter_templateexamplevalue_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="templateexamplevalue",
            options={
                "verbose_name": "Example Value",
                "verbose_name_plural": "Example Value",
            },
        ),
        migrations.AlterField(
            model_name="whatsapptemplate",
            name="example_values",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="example_values",
                to="home.templateexamplevalue",
            ),
        ),
    ]
