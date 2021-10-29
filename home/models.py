from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.api import APIField
from wagtail.core.models import Page, PageRevision
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.api.fields import ImageRenditionField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    StreamFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail_content_import.models import ContentImportMixin
from wagtailmedia.blocks import AbstractMediaChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock


class MediaBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        pass


class WhatsappBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    document = DocumentChooserBlock(icon="document", required=False)
    media = MediaBlock(icon="media", required=False)
    message = blocks.TextBlock(
        max_lenth=4096, help_text="each message cannot exceed 4096 characters."
    )

    class Meta:
        icon = "user"
        form_classname = "whatsapp-message-block struct-block"


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


class ContentPage(Page, ContentImportMixin):
    parent_page_type = [
        "ContentPageIndex",
    ]

    # general page attributes
    tags = ClusterTaggableManager(through=ContentPageTag)
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
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    body = RichTextField(blank=True, null=True)
    include_in_footer = models.BooleanField(default=False)

    # Web panels
    web_panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("subtitle"),
                ImageChooserPanel('feed_image'),
                StreamFieldPanel("body"),
                FieldPanel("include_in_footer"),
            ],
            heading="Web",
        ),
    ]

    # whatsapp page setup
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
    )

    # whatsapp panels
    whatsapp_panels = [
        MultiFieldPanel(
            [
                FieldPanel("whatsapp_title"),
                StreamFieldPanel("whatsapp_body"),
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
    )

    # messenger panels
    messenger_panels = [
        MultiFieldPanel(
            [
                FieldPanel("messenger_title"),
                StreamFieldPanel("messenger_body"),
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
    )

    # viber panels
    viber_panels = [
        MultiFieldPanel(
            [
                FieldPanel("viber_title"),
                StreamFieldPanel("viber_body"),
            ],
            heading="Viber",
        ),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel("tags"),
    ]
    settings_panels = Page.settings_panels + [
        FieldPanel("enable_web"),
        FieldPanel("enable_whatsapp"),
        FieldPanel("enable_messenger"),
        FieldPanel("enable_viber"),
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
        APIField('feed_image_thumbnail', serializer=ImageRenditionField('fill-100x100', source='feed_image')),
        APIField("body"),
        APIField("tags"),
        APIField("has_children"),
    ]

    @property
    def has_children(self):
        return self.get_children_count() > 0

    @property
    def page_rating(self):
        return self._calc_avg_rating(self.ratings.all())

    @property
    def latest_revision_rating(self):
        return self._calc_avg_rating(
            self.ratings.filter(revision=self.get_latest_revision())
        )

    def _calc_avg_rating(self, ratings):
        if ratings:
            helpful = 0
            for rating in ratings:
                if rating.helpful:
                    helpful += 1

            return int(helpful / ratings.count() * 100)


class ContentPageRating(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    page = models.ForeignKey(
        ContentPage, related_name="ratings", null=False, on_delete=models.CASCADE
    )
    revision = models.ForeignKey(
        PageRevision, related_name="ratings", null=False, on_delete=models.CASCADE
    )
    helpful = models.BooleanField()
    comment = models.TextField(blank=True, default="")
    data = models.JSONField(default=dict, blank=True, null=True)
