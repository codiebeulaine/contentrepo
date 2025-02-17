# Generated by Django 4.2.17 on 2025-02-17 07:41

from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0089_alter_assessment_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderedcontentset",
            name="pages",
            field=wagtail.fields.StreamField(
                [
                    (
                        "pages",
                        wagtail.blocks.StructBlock(
                            [
                                ("contentpage", wagtail.blocks.PageChooserBlock()),
                                (
                                    "time",
                                    wagtail.blocks.IntegerBlock(
                                        help_text="When should this message be sent? Set the number of  hours, days, months or year.",
                                        min_value=0,
                                        required=False,
                                    ),
                                ),
                                (
                                    "unit",
                                    wagtail.blocks.ChoiceBlock(
                                        choices=[
                                            ("minutes", "Minutes"),
                                            ("hours", "Hours"),
                                            ("days", "Days"),
                                            ("months", "Months"),
                                        ],
                                        help_text="Choose the unit of time to use.",
                                        required=False,
                                    ),
                                ),
                                (
                                    "before_or_after",
                                    wagtail.blocks.ChoiceBlock(
                                        choices=[
                                            ("after", "After"),
                                            ("before", "Before"),
                                        ],
                                        help_text="Is it ‘before’ or ‘after’ the reference point for your timings, which is set in the contact field below.",
                                        required=False,
                                    ),
                                ),
                                (
                                    "contact_field",
                                    wagtail.blocks.CharBlock(
                                        help_text="This is the reference point used to base the timing of message on. For example, edd (estimated date of birth) or dob (date of birth).",
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
                null=True,
                use_json_field=True,
            ),
        ),
    ]
