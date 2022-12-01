# Generated by Django 4.1.1 on 2022-12-01 14:40

from django.db import migrations, models
import django.db.models.deletion
import home.models
import wagtail.blocks
import wagtail.documents.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0076_modellogentry_revision"),
        ("home", "0022_merge_20220927_1207"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contentpage",
            name="whatsapp_body",
            field=wagtail.fields.StreamField(
                [
                    (
                        "Whatsapp_Message",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "image",
                                    wagtail.images.blocks.ImageChooserBlock(
                                        required=False
                                    ),
                                ),
                                (
                                    "document",
                                    wagtail.documents.blocks.DocumentChooserBlock(
                                        icon="document", required=False
                                    ),
                                ),
                                (
                                    "media",
                                    home.models.MediaBlock(
                                        icon="media", required=False
                                    ),
                                ),
                                (
                                    "message",
                                    wagtail.blocks.TextBlock(
                                        help_text="each message cannot exceed 4096 characters.",
                                        max_lenth=4096,
                                    ),
                                ),
                                (
                                    "variation_messages",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.StructBlock(
                                            [
                                                (
                                                    "variation_message",
                                                    wagtail.blocks.ChoiceBlock(
                                                        choices=home.models.get_choices,
                                                        required=False,
                                                    ),
                                                ),
                                                (
                                                    "message",
                                                    wagtail.blocks.TextBlock(
                                                        help_text="each message cannot exceed 4096 characters.",
                                                        max_lenth=4096,
                                                    ),
                                                ),
                                            ]
                                        )
                                    ),
                                ),
                                (
                                    "next_prompt",
                                    wagtail.blocks.CharBlock(
                                        help_text="prompt text for next message",
                                        max_length=20,
                                        required=False,
                                    ),
                                ),
                            ],
                            help_text="Each message will be sent with the text and media",
                        ),
                    )
                ],
                blank=True,
                null=True,
                use_json_field=True,
            ),
        ),
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "content_variations_options",
                    wagtail.fields.StreamField(
                        [("content_variations_options", wagtail.blocks.CharBlock())],
                        blank=True,
                        null=True,
                        use_json_field=None,
                    ),
                ),
                (
                    "site",
                    models.OneToOneField(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wagtailcore.site",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
