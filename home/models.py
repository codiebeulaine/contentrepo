from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import CheckboxSelectMultiple
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import ItemBase, TagBase, TaggedItemBase
from wagtail import blocks
from wagtail.api import APIField
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page, Revision
from wagtail.models.sites import Site
from wagtail.search import index
from wagtail_content_import.models import ContentImportMixin
from wagtailmedia.blocks import AbstractMediaChooserBlock

from .constants import AGE_CHOICES, GENDER_CHOICES, RELATIONSHIP_STATUS_CHOICES
from .panels import PageRatingPanel
from .whatsapp import create_whatsapp_template

from wagtail.admin.panels import (  # isort:skip
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)


@register_setting
class SiteSettings(BaseSiteSetting):
    title = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text="The branding title shown in the CMS",
    )
    login_message = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="The login message shown on the login page",
    )
    welcome_message = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="The welcome message shown after logging in",
    )
    logo = models.ImageField(blank=True, null=True, upload_to="images")
    favicon = models.ImageField(blank=True, null=True, upload_to="images")
    profile_field_options = StreamField(
        [
            (
                "gender",
                blocks.MultipleChoiceBlock(
                    choices=GENDER_CHOICES, widget=CheckboxSelectMultiple
                ),
            ),
            (
                "age",
                blocks.MultipleChoiceBlock(
                    choices=AGE_CHOICES, widget=CheckboxSelectMultiple
                ),
            ),
            (
                "relationship",
                blocks.MultipleChoiceBlock(
                    choices=RELATIONSHIP_STATUS_CHOICES, widget=CheckboxSelectMultiple
                ),
            ),
        ],
        blank=True,
        null=True,
        help_text="Fields that may be used to restrict content to certain user segments",
        use_json_field=True,
        block_counts={
            "gender": {"max_num": 1},
            "age": {"max_num": 1},
            "relationship": {"max_num": 1},
        },
    )

    first_tab_panels = [
        FieldPanel("title"),
        FieldPanel("login_message"),
        FieldPanel("welcome_message"),
        FieldPanel("logo"),
        FieldPanel("favicon"),
    ]
    second_tab_panels = [
        FieldPanel("profile_field_options"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(first_tab_panels, heading="Branding"),
            ObjectList(second_tab_panels, heading="Profiling"),
        ]
    )


class MediaBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        pass


def get_valid_profile_values(field):
    site = Site.objects.get(is_default_site=True)
    site_settings = SiteSettings.for_site(site)

    profile_values = {}

    for profile_block in site_settings.profile_field_options:
        profile_values[profile_block.block_type] = [b for b in profile_block.value]
    try:
        return profile_values[field]
    except KeyError:
        return []


def get_gender_choices():
    # Wrapper for get_profile_field_choices that can be passed as a callable
    choices = {k: v for k, v in GENDER_CHOICES}
    return [(g, choices[g]) for g in get_valid_profile_values("gender")]


def get_age_choices():
    # Wrapper for get_profile_field_choices that can be passed as a callable
    choices = {k: v for k, v in AGE_CHOICES}
    return [(a, choices[a]) for a in get_valid_profile_values("age")]


def get_relationship_choices():
    # Wrapper for get_profile_field_choices that can be passed as a callable
    choices = {k: v for k, v in RELATIONSHIP_STATUS_CHOICES}
    return [(r, choices[r]) for r in get_valid_profile_values("relationship")]


class VariationBlock(blocks.StructBlock):
    variation_restrictions = blocks.StreamBlock(
        [
            ("gender", blocks.ChoiceBlock(choices=get_gender_choices)),
            ("age", blocks.ChoiceBlock(choices=get_age_choices)),
            ("relationship", blocks.ChoiceBlock(choices=get_relationship_choices)),
        ],
        required=False,
        min_num=1,
        max_num=1,
        help_text="Restrict this variation to users with this profile value. Valid values must be added to the Site Settings",
        use_json_field=True,
    )
    message = blocks.TextBlock(
        max_lenth=4096,
        help_text="each message cannot exceed 4096 characters.",
    )


class WhatsappBlock(blocks.StructBlock):
    MEDIA_CAPTION_MAX_LENGTH = 1024

    image = ImageChooserBlock(required=False)
    document = DocumentChooserBlock(icon="document", required=False)
    media = MediaBlock(icon="media", required=False)
    message = blocks.TextBlock(
        max_lenth=4096, help_text="each message cannot exceed 4096 characters."
    )
    variation_messages = blocks.ListBlock(VariationBlock(), default=[])
    next_prompt = blocks.CharBlock(
        max_length=20, help_text="prompt text for next message", required=False
    )

    class Meta:
        icon = "user"
        form_classname = "whatsapp-message-block struct-block"

    def clean(self, value):
        result = super().clean(value)

        if (
            result["image"]
            or result["document"]
            or result["media"]
            and len(result["message"] > self.MEDIA_CAPTION_MAX_LENGTH)
        ):
            raise StructBlockValidationError(
                {
                    "message": ValidationError(
                        "A WhatsApp message with media cannot be longer than "
                        f"{self.MEDIA_CAPTION_MAX_LENGTH} characters, your message is "
                        f"{len(result['message'])} characters long"
                    )
                }
            )
        return result


class ViberBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    message = blocks.TextBlock(
        max_lenth=7000, help_text="each message cannot exceed 7000 characters."
    )

    class Meta:
        icon = "user"
        form_classname = "whatsapp-message-block struct-block"


class MessengerBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    message = blocks.TextBlock(
        max_lenth=2000, help_text="each message cannot exceed 2000 characters."
    )

    class Meta:
        icon = "user"
        form_classname = "whatsapp-message-block struct-block"


class HomePage(Page):
    subpage_types = [
        "ContentPageIndex",
    ]


class ContentPageIndex(Page):
    subpage_types = [
        "ContentPage",
    ]

    include_in_homepage = models.BooleanField(default=False)

    @property
    def has_children(self):
        return self.get_children_count() > 0

    api_fields = [
        APIField("title"),
        APIField("include_in_homepage"),
        APIField("has_children"),
    ]


class ContentPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "ContentPage", on_delete=models.CASCADE, related_name="tagged_items"
    )


class ContentTrigger(TagBase):
    class Meta:
        verbose_name = "content trigger"
        verbose_name_plural = "content triggers"


class TriggeredContent(ItemBase):
    tag = models.ForeignKey(
        ContentTrigger, related_name="triggered_content", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="home.ContentPage", on_delete=models.CASCADE, related_name="triggered_items"
    )


class ContentQuickReply(TagBase):
    class Meta:
        verbose_name = "quick reply"
        verbose_name_plural = "quick replies"


class QuickReplyContent(ItemBase):
    tag = models.ForeignKey(
        ContentQuickReply, related_name="quick_reply_content", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="home.ContentPage",
        on_delete=models.CASCADE,
        related_name="quick_reply_items",
    )


class ContentPage(Page, ContentImportMixin):
    parent_page_type = [
        "ContentPageIndex",
    ]

    # general page attributes
    tags = ClusterTaggableManager(through=ContentPageTag, blank=True)
    triggers = ClusterTaggableManager(through="home.TriggeredContent", blank=True)
    quick_replies = ClusterTaggableManager(through="home.QuickReplyContent", blank=True)
    related_pages = StreamField(
        [
            ("related_page", blocks.PageChooserBlock()),
        ],
        blank=True,
        null=True,
        use_json_field=True,
    )
    enable_web = models.BooleanField(
        default=False, help_text="When enabled, the API will include the web content"
    )
    enable_whatsapp = models.BooleanField(
        default=False,
        help_text="When enabled, the API will include the whatsapp content",
    )
    enable_messenger = models.BooleanField(
        default=False,
        help_text="When enabled, the API will include the messenger content",
    )
    enable_viber = models.BooleanField(
        default=False, help_text="When enabled, the API will include the viber content"
    )

    # Web page setup
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    body = StreamField(
        [
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        blank=True,
        null=True,
        use_json_field=True,
    )
    include_in_footer = models.BooleanField(default=False)

    # Web panels
    web_panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("subtitle"),
                FieldPanel("body"),
                FieldPanel("include_in_footer"),
            ],
            heading="Web",
        ),
    ]

    # whatsapp page setup
    is_whatsapp_template = models.BooleanField("Is Template", default=False)
    whatsapp_template_name = models.CharField(max_length=512, blank=True, default="")
    whatsapp_title = models.CharField(max_length=200, blank=True, null=True)
    whatsapp_body = StreamField(
        [
            (
                "Whatsapp_Message",
                WhatsappBlock(
                    help_text="Each message will be sent with the text and media"
                ),
            ),
        ],
        blank=True,
        null=True,
        use_json_field=True,
    )

    # whatsapp panels
    whatsapp_panels = [
        MultiFieldPanel(
            [
                FieldPanel("whatsapp_title"),
                FieldPanel("is_whatsapp_template"),
                FieldPanel("whatsapp_body"),
            ],
            heading="Whatsapp",
        ),
    ]

    # messenger page setup
    messenger_title = models.CharField(max_length=200, blank=True, null=True)
    messenger_body = StreamField(
        [
            (
                "messenger_block",
                MessengerBlock(
                    help_text="Each paragraph cannot extend "
                    "over the messenger message "
                    "limit of 2000 characters"
                ),
            ),
        ],
        blank=True,
        null=True,
        use_json_field=True,
    )

    # messenger panels
    messenger_panels = [
        MultiFieldPanel(
            [
                FieldPanel("messenger_title"),
                FieldPanel("messenger_body"),
            ],
            heading="Messenger",
        ),
    ]

    # viber page setup
    viber_title = models.CharField(max_length=200, blank=True, null=True)
    viber_body = StreamField(
        [
            (
                "viber_message",
                ViberBlock(
                    help_text="Each paragraph cannot extend "
                    "over the viber message limit "
                    "of 7000 characters"
                ),
            ),
        ],
        blank=True,
        null=True,
        use_json_field=True,
    )

    # viber panels
    viber_panels = [
        MultiFieldPanel(
            [
                FieldPanel("viber_title"),
                FieldPanel("viber_body"),
            ],
            heading="Viber",
        ),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel("tags"),
        FieldPanel("triggers", heading="Triggers"),
        FieldPanel("quick_replies", heading="Quick Replies"),
        PageRatingPanel("Rating"),
        FieldPanel("related_pages"),
    ]
    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [
                FieldPanel("enable_web"),
                FieldPanel("enable_whatsapp"),
                FieldPanel("enable_messenger"),
                FieldPanel("enable_viber"),
            ],
            heading="API settings",
        ),
    ]
    edit_handler = TabbedInterface(
        [
            ObjectList(web_panels, heading="Web"),
            ObjectList(whatsapp_panels, heading="Whatsapp"),
            ObjectList(messenger_panels, heading="Messenger"),
            ObjectList(viber_panels, heading="Viber"),
            ObjectList(promote_panels, heading="Promotional"),
            ObjectList(settings_panels, heading="Settings"),
        ]
    )

    api_fields = [
        APIField("title"),
        APIField("subtitle"),
        APIField("body"),
        APIField("tags"),
        APIField("triggers"),
        APIField("quick_replies"),
        APIField("related_pages"),
        APIField("has_children"),
    ]

    @property
    def has_children(self):
        return self.get_children_count() > 0

    @property
    def page_rating(self):
        return self._calc_avg_rating(self.ratings.all())

    @property
    def view_count(self):
        return self.views.count()

    @property
    def latest_revision_rating(self):
        return self._calc_avg_rating(
            self.ratings.filter(revision=self.get_latest_revision())
        )

    @property
    def whatsapp_template_prefix(self):
        return self.whatsapp_title.replace(" ", "_")

    @property
    def whatsapp_template_body(self):
        return self.whatsapp_body.raw_data[0]["value"]["message"]

    def create_whatsapp_template_name(self) -> str:
        return f"{self.whatsapp_template_prefix}_{self.get_latest_revision().pk}"

    def get_descendants(self, inclusive=False):
        return ContentPage.objects.descendant_of(self, inclusive)

    def _calc_avg_rating(self, ratings):
        if ratings:
            helpful = 0
            for rating in ratings:
                if rating.helpful:
                    helpful += 1

            percentage = int(helpful / ratings.count() * 100)
            return f"{helpful}/{ratings.count()} ({percentage}%)"
        return "(no ratings yet)"

    def save_page_view(self, query_params, platform=None):
        if not platform and query_params:
            if "whatsapp" in query_params:
                platform = "whatsapp"
            elif "messenger" in query_params:
                platform = "messenger"
            elif "viber" in query_params:
                platform = "viber"
            else:
                platform = "web"

        data = {}
        for param, value in query_params.items():
            if param.startswith("data__"):
                key = param.replace("data__", "")
                data[key] = value

        page_view = {
            "revision": self.get_latest_revision(),
            "data": data,
            "platform": f"{platform}",
        }

        if "message" in query_params and query_params["message"].isdigit():
            page_view["message"] = query_params["message"]

        self.views.create(**page_view)

    @property
    def quick_reply_buttons(self):
        return self.quick_reply_items.all().values_list("tag__name", flat=True)

    def submit_whatsapp_template(self, previous_revision):
        """
        Submits a request to the WhatsApp API to create a template for this content

        Only submits if the create templates is enabled, if the page is a whatsapp
        template, and if the content or buttons are different to the previous revision
        """
        if not settings.WHATSAPP_CREATE_TEMPLATES:
            return
        if not self.is_whatsapp_template:
            return
        try:
            previous_revision = previous_revision.as_object()
            if (
                self.whatsapp_template_body == previous_revision.whatsapp_template_body
                and sorted(self.quick_reply_buttons)
                == sorted(previous_revision.quick_reply_buttons)
                and self.is_whatsapp_template == previous_revision.is_whatsapp_template
            ):
                return
        except AttributeError:
            pass

        self.whatsapp_template_name = self.create_whatsapp_template_name()

        create_whatsapp_template(
            self.whatsapp_template_name,
            self.whatsapp_template_body,
            sorted(self.quick_reply_buttons),
        )

        return self.whatsapp_template_name

    def save_revision(
        self,
        user=None,
        submitted_for_moderation=False,
        approved_go_live_at=None,
        changed=True,
        log_action=False,
        previous_revision=None,
        clean=True,
    ):
        previous_revision = self.get_latest_revision()
        revision = super().save_revision(
            user,
            submitted_for_moderation,
            approved_go_live_at,
            changed,
            log_action,
            previous_revision,
            clean,
        )
        template_name = self.submit_whatsapp_template(previous_revision)
        if template_name:
            revision.content["whatsapp_template_name"] = template_name
            revision.save(update_fields=["content"])
        return revision


class OrderedContentSet(index.Indexed, models.Model):
    name = models.CharField(
        max_length=255, help_text="The name of the ordered content set."
    )

    def get_gender(self):
        for item in self.profile_fields.raw_data:
            if item["type"] == "gender":
                return item["value"]

    def get_age(self):
        for item in self.profile_fields.raw_data:
            if item["type"] == "age":
                return item["value"]

    def get_relationship(self):
        for item in self.profile_fields.raw_data:
            if item["type"] == "relationship":
                return item["value"]

    profile_fields = StreamField(
        [
            ("gender", blocks.ChoiceBlock(choices=get_gender_choices)),
            ("age", blocks.ChoiceBlock(choices=get_age_choices)),
            ("relationship", blocks.ChoiceBlock(choices=get_relationship_choices)),
        ],
        help_text="Restrict this ordered set to users with these profile values. Valid values must be added to the Site Settings",
        use_json_field=True,
        block_counts={
            "gender": {"max_num": 1},
            "age": {"max_num": 1},
            "relationship": {"max_num": 1},
        },
        default=[],
        blank=True,
    )
    search_fields = [
        index.SearchField("name", partial_match=True),
        index.SearchField("get_gender", partial_match=True),
        index.SearchField("get_age", partial_match=True),
        index.SearchField("get_relationship", partial_match=True),
    ]
    pages = StreamField(
        [
            (
                "pages",
                blocks.StructBlock(
                    [
                        ("contentpage", blocks.PageChooserBlock()),
                        ("time", blocks.IntegerBlock(min_value=0, required=False)),
                        (
                            "unit",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("minutes", "Minutes"),
                                    ("hours", "Hours"),
                                    ("days", "Days"),
                                    ("months", "Months"),
                                ],
                                required=False,
                            ),
                        ),
                        (
                            "before_or_after",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("after", "After"),
                                    ("before", "Before"),
                                ],
                                required=False,
                            ),
                        ),
                        (
                            "contact_field",
                            blocks.CharBlock(
                                required=False,
                            ),
                        ),
                    ]
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
        null=True,
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("profile_fields"),
        FieldPanel("pages"),
    ]

    api_fields = [
        APIField("name"),
        APIField("profile_fields"),
        APIField("pages"),
    ]

    def __str__(self):
        """String repr of this snippet."""
        return self.name

    class Meta:  # noqa
        verbose_name = "Ordered Content Set"
        verbose_name_plural = "Ordered Content Sets"


class ContentPageRating(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    page = models.ForeignKey(
        ContentPage, related_name="ratings", null=False, on_delete=models.CASCADE
    )
    revision = models.ForeignKey(
        Revision, related_name="ratings", null=False, on_delete=models.CASCADE
    )
    helpful = models.BooleanField()
    comment = models.TextField(blank=True, default="")
    data = models.JSONField(default=dict, blank=True, null=True)


class PageView(models.Model):
    platform = models.CharField(
        choices=[
            ("WHATSAPP", "whatsapp"),
            ("VIBER", "viber"),
            ("MESSENGER", "messenger"),
            ("WEB", "web"),
        ],
        null=True,
        blank=True,
        default="web",
        max_length=20,
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    page = models.ForeignKey(
        ContentPage, related_name="views", null=False, on_delete=models.CASCADE
    )
    revision = models.ForeignKey(
        Revision, related_name="views", null=False, on_delete=models.CASCADE
    )
    message = models.IntegerField(blank=True, default=None, null=True)
    data = models.JSONField(default=dict, blank=True, null=True)
