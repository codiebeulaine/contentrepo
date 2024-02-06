# Generated by Django 4.1.13 on 2024-01-30 15:25

import django.core.validators
import wagtail.blocks
import wagtail.documents.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations

import home.models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0047_alter_contentpage_messenger_title_and_more"),
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
                                        help_text="each text message cannot exceed 4096 characters, messages with media cannot exceed 1024 characters.",
                                        validators=(
                                            django.core.validators.MaxLengthValidator(
                                                4096
                                            ),
                                        ),
                                    ),
                                ),
                                (
                                    "example_values",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.CharBlock(label="Example Value"),
                                        default=[],
                                        help_text="Please add example values for all variables used in a WhatsApp template",
                                        label="Variable Example Values",
                                    ),
                                ),
                                (
                                    "variation_messages",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.StructBlock(
                                            [
                                                (
                                                    "variation_restrictions",
                                                    wagtail.blocks.StreamBlock(
                                                        [
                                                            (
                                                                "gender",
                                                                wagtail.blocks.ChoiceBlock(
                                                                    choices=home.models.get_gender_choices
                                                                ),
                                                            ),
                                                            (
                                                                "age",
                                                                wagtail.blocks.ChoiceBlock(
                                                                    choices=home.models.get_age_choices
                                                                ),
                                                            ),
                                                            (
                                                                "relationship",
                                                                wagtail.blocks.ChoiceBlock(
                                                                    choices=home.models.get_relationship_choices
                                                                ),
                                                            ),
                                                        ],
                                                        help_text="Restrict this variation to users with this profile value. Valid values must be added to the Site Settings",
                                                        max_num=1,
                                                        min_num=1,
                                                        required=False,
                                                        use_json_field=True,
                                                    ),
                                                ),
                                                (
                                                    "message",
                                                    wagtail.blocks.TextBlock(
                                                        help_text="each message cannot exceed 4096 characters.",
                                                        validators=(
                                                            django.core.validators.MaxLengthValidator(
                                                                4096
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ]
                                        ),
                                        default=[],
                                    ),
                                ),
                                (
                                    "next_prompt",
                                    wagtail.blocks.CharBlock(
                                        help_text="prompt text for next message",
                                        required=False,
                                        validators=(
                                            django.core.validators.MaxLengthValidator(
                                                20
                                            ),
                                        ),
                                    ),
                                ),
                                (
                                    "buttons",
                                    wagtail.blocks.StreamBlock(
                                        [
                                            (
                                                "next_message",
                                                wagtail.blocks.StructBlock(
                                                    [
                                                        (
                                                            "title",
                                                            wagtail.blocks.CharBlock(
                                                                help_text="text for the button, up to 20 characters.",
                                                                validators=(
                                                                    django.core.validators.MaxLengthValidator(
                                                                        20
                                                                    ),
                                                                ),
                                                            ),
                                                        )
                                                    ]
                                                ),
                                            ),
                                            (
                                                "go_to_page",
                                                wagtail.blocks.StructBlock(
                                                    [
                                                        (
                                                            "title",
                                                            wagtail.blocks.CharBlock(
                                                                help_text="text for the button, up to 20 characters.",
                                                                validators=(
                                                                    django.core.validators.MaxLengthValidator(
                                                                        20
                                                                    ),
                                                                ),
                                                            ),
                                                        ),
                                                        (
                                                            "page",
                                                            wagtail.blocks.PageChooserBlock(
                                                                help_text="page the button should go to"
                                                            ),
                                                        ),
                                                    ]
                                                ),
                                            ),
                                        ],
                                        max_num=3,
                                        required=False,
                                    ),
                                ),
                                (
                                    "list_items",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.CharBlock(label="Title"),
                                        default=[],
                                        help_text="List item title, up to 24 characters.",
                                        max_num=10,
                                        required=False,
                                        validators=django.core.validators.MaxLengthValidator(
                                            24
                                        ),
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
    ]
