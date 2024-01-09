# Generated by Django 4.1.13 on 2024-01-08 10:11

from django.db import migrations, models


def update_template_names(ContentPage, ContentType, Revision):
    """
     Update historic data template names to lower case
    """
    for page in ContentPage.objects.filter(is_whatsapp_template=True):
        if not page.whatsapp_title:
            continue
        template_prefix = page.whatsapp_title.lower().replace(" ", "_")
        page.whatsapp_template_name = f"{template_prefix}_{page.latest_revision.id}"
        page.save(update_fields=["whatsapp_template_name"])

    content_type = ContentType.objects.get_for_model(ContentPage)
    for revision in Revision.objects.filter(content_type__pk=content_type.pk):
        if not revision.content.get("whatsapp_title"):
            continue
        if not revision.content.get("is_whatsapp_template"):
            continue
        template_prefix = revision.content["whatsapp_title"].lower().replace(" ", "_")
        revision.content["whatsapp_template_name"] = f"{template_prefix}_{revision.pk}"
        revision.save(update_fields=["content"])


def run_migration(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    ContentPage = apps.get_model("home", "ContentPage")
    Revision = apps.get_model("wagtailcore", "Revision")
    update_template_names(ContentType, ContentPage, Revision)


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0040_alter_contentpage_whatsapp_template_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contentpage",
            name="whatsapp_template_name",
            field=models.CharField(max_length=512, blank=True, default=""),
        ),
    ]
