# Generated by Django 4.2.11 on 2024-11-25 12:05

from django.db import migrations, models
from django.db.models import Count
import django.db.models.deletion


def rename_duplicate_slugs(OrderedContentSet):
    duplicate_slugs = (
        OrderedContentSet.objects.values("slug", "locale")
        .annotate(count=Count("slug"))
        .order_by("-count")
        .filter(count__gt=1)
        .values_list("slug", "locale")
    )
    for slug, locale in duplicate_slugs:
        pages = OrderedContentSet.objects.filter(slug=slug, locale=locale)
        while pages.count() > 1:
            page = pages.first()

            suffix = 1
            candidate_slug = slug
            while OrderedContentSet.objects.filter(
                slug=candidate_slug, locale=locale
            ).exists():
                suffix += 1
                candidate_slug = f"{slug}-{suffix}"

            page.slug = candidate_slug
            page.save(update_fields=["slug"])


def set_locale_from_instance(OrderedContentSet, Site):
    site = Site.objects.get(is_default_site=True)
    for ocs in OrderedContentSet.objects.all():
        if ocs.pages:
            # Get the first page's data
            first_page_data = ocs.pages[0]
            contentpage = first_page_data.value.get("contentpage")
            if contentpage:
                ocs.locale = contentpage.locale
            else:
                ocs.locale = site.root_page.locale
        else:
            ocs.locale = site.root_page.locale
        ocs.save(update_fields=["locale"])


def run_migration(apps, schema_editor):
    OrderedContentSet = apps.get_model("home", "OrderedContentSet")
    Site = apps.get_model("wagtailcore", "Site")
    rename_duplicate_slugs(OrderedContentSet)
    set_locale_from_instance(OrderedContentSet, Site)


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("home", "0084_alter_contentpage_whatsapp_body"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderedcontentset",
            name="locale",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                to="wagtailcore.locale",
            ),
        ),
        migrations.AddField(
            model_name="orderedcontentset",
            name="slug",
            field=models.SlugField(
                default="",
                help_text="A unique identifier for this ordered content set",
                max_length=255,
            ),
        ),
        migrations.RunPython(
            code=run_migration, reverse_code=migrations.RunPython.noop
        ),
    ]