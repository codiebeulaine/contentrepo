# Generated by Django 4.2.11 on 2024-09-17 11:43

from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0081_remove_contentpage_embedding"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assessment",
            name="questions",
            field=wagtail.fields.StreamField(
                [
                    (
                        "categorical_question",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "question",
                                    wagtail.blocks.TextBlock(
                                        help_text="The question to ask the user"
                                    ),
                                ),
                                (
                                    "explainer",
                                    wagtail.blocks.TextBlock(
                                        help_text="Explainer message which tells the user why we need this question",
                                        required=False,
                                    ),
                                ),
                                (
                                    "error",
                                    wagtail.blocks.TextBlock(
                                        help_text="Error message for this question if we don't understand the input",
                                        required=False,
                                    ),
                                ),
                                (
                                    "question_semantic_id",
                                    wagtail.blocks.TextBlock(
                                        help_text="Semantic ID for this question"
                                    ),
                                ),
                                (
                                    "answers",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.StructBlock(
                                            [
                                                (
                                                    "answer",
                                                    wagtail.blocks.TextBlock(
                                                        help_text="The choice shown to the user for this option"
                                                    ),
                                                ),
                                                (
                                                    "score",
                                                    wagtail.blocks.FloatBlock(
                                                        help_text="How much to add to the total score if this answer is chosen"
                                                    ),
                                                ),
                                                (
                                                    "answer_semantic_id",
                                                    wagtail.blocks.TextBlock(
                                                        help_text="Semantic ID for this answer"
                                                    ),
                                                ),
                                            ]
                                        )
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "age_question",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "question",
                                    wagtail.blocks.TextBlock(
                                        help_text="The question to ask the user"
                                    ),
                                ),
                                (
                                    "explainer",
                                    wagtail.blocks.TextBlock(
                                        help_text="Explainer message which tells the user why we need this question",
                                        required=False,
                                    ),
                                ),
                                (
                                    "error",
                                    wagtail.blocks.TextBlock(
                                        help_text="Error message for this question if we don't understand the input",
                                        required=False,
                                    ),
                                ),
                                (
                                    "question_semantic_id",
                                    wagtail.blocks.TextBlock(
                                        help_text="Semantic ID for this question"
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "multiselect_question",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "question",
                                    wagtail.blocks.TextBlock(
                                        help_text="The question to ask the user"
                                    ),
                                ),
                                (
                                    "explainer",
                                    wagtail.blocks.TextBlock(
                                        help_text="Explainer message which tells the user why we need this question",
                                        required=False,
                                    ),
                                ),
                                (
                                    "error",
                                    wagtail.blocks.TextBlock(
                                        help_text="Error message for this question if we don't understand the input",
                                        required=False,
                                    ),
                                ),
                                (
                                    "question_semantic_id",
                                    wagtail.blocks.TextBlock(
                                        help_text="Semantic ID for this question"
                                    ),
                                ),
                                (
                                    "answers",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.StructBlock(
                                            [
                                                (
                                                    "answer",
                                                    wagtail.blocks.TextBlock(
                                                        help_text="The choice shown to the user for this option"
                                                    ),
                                                ),
                                                (
                                                    "score",
                                                    wagtail.blocks.FloatBlock(
                                                        help_text="How much to add to the total score if this answer is chosen"
                                                    ),
                                                ),
                                                (
                                                    "answer_semantic_id",
                                                    wagtail.blocks.TextBlock(
                                                        help_text="Semantic ID for this answer"
                                                    ),
                                                ),
                                            ]
                                        )
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "freetext_question",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "question",
                                    wagtail.blocks.TextBlock(
                                        help_text="The question to ask the user"
                                    ),
                                ),
                                (
                                    "explainer",
                                    wagtail.blocks.TextBlock(
                                        help_text="Explainer message which tells the user why we need this question",
                                        required=False,
                                    ),
                                ),
                                (
                                    "question_semantic_id",
                                    wagtail.blocks.TextBlock(
                                        help_text="Semantic ID for this question"
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "integer_question",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "question",
                                    wagtail.blocks.TextBlock(
                                        help_text="The question to ask the user"
                                    ),
                                ),
                                (
                                    "explainer",
                                    wagtail.blocks.TextBlock(
                                        help_text="Explainer message which tells the user why we need this question",
                                        required=False,
                                    ),
                                ),
                                (
                                    "error",
                                    wagtail.blocks.TextBlock(
                                        help_text="Error message for this question if we don't understand the input",
                                        required=False,
                                    ),
                                ),
                                (
                                    "question_semantic_id",
                                    wagtail.blocks.TextBlock(
                                        help_text="Semantic ID for this question"
                                    ),
                                ),
                                (
                                    "min",
                                    wagtail.blocks.IntegerBlock(
                                        default=None,
                                        help_text="The minimum value that can be entered",
                                    ),
                                ),
                                (
                                    "max",
                                    wagtail.blocks.IntegerBlock(
                                        default=None,
                                        help_text="The maximum value that can be entered",
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "year_of_birth_question",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "question",
                                    wagtail.blocks.TextBlock(
                                        help_text="The question to ask the user"
                                    ),
                                ),
                                (
                                    "explainer",
                                    wagtail.blocks.TextBlock(
                                        help_text="Explainer message which tells the user why we need this question",
                                        required=False,
                                    ),
                                ),
                                (
                                    "error",
                                    wagtail.blocks.TextBlock(
                                        help_text="Error message for this question if we don't understand the input",
                                        required=False,
                                    ),
                                ),
                                (
                                    "question_semantic_id",
                                    wagtail.blocks.TextBlock(
                                        help_text="Semantic ID for this question"
                                    ),
                                ),
                            ]
                        ),
                    ),
                ],
                use_json_field=True,
            ),
        ),
    ]
