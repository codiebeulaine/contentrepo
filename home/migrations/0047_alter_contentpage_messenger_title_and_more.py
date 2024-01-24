# Generated by Django 4.1.13 on 2024-01-24 05:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0046_alter_contentpage_whatsapp_body"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contentpage",
            name="messenger_title",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AlterField(
            model_name="contentpage",
            name="subtitle",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AlterField(
            model_name="contentpage",
            name="viber_title",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AlterField(
            model_name="contentpage",
            name="whatsapp_title",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AlterField(
            model_name="pageview",
            name="platform",
            field=models.CharField(
                blank=True,
                choices=[
                    ("WHATSAPP", "whatsapp"),
                    ("SMS", "sms"),
                    ("USSD", "ussd"),
                    ("VIBER", "viber"),
                    ("MESSENGER", "messenger"),
                    ("WEB", "web"),
                ],
                default="web",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="login_message",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The login message shown on the login page",
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="title",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The branding title shown in the CMS",
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="welcome_message",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The welcome message shown after logging in",
                max_length=100,
            ),
        ),
    ]
