# Generated by Django 4.2.11 on 2024-03-19 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0057_alter_templateexamplevalue_options_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="whatsapptemplate",
            name="example_values",
        ),
        migrations.AddField(
            model_name="whatsapptemplate",
            name="example_values",
            field=models.ManyToManyField(to="home.templateexamplevalue"),
        ),
    ]
