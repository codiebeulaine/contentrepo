from django.template.defaultfilters import truncatechars
from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin import widgets as wagtailadmin_widgets
from wagtail.admin.menu import AdminOnlyMenuItem
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from wagtail.admin.panels import FieldPanel, MultiFieldPanel  # isort:skip

from .models import ContentPage, OrderedContentSet, WhatsAppTemplate

from .views import (  # isort:skip
    ContentPageReportView,
    CustomIndexView,
    OrderedContentSetUploadView,
    PageViewReportView,
    ContentUploadView,
)


@hooks.register("register_admin_urls")
def register_import_urls():
    return [
        path("import/", ContentUploadView.as_view(), name="import"),
        path(
            "import_orderedcontentset/",
            OrderedContentSetUploadView.as_view(),
            name="import_orderedcontentset",
        ),
    ]


@hooks.register("register_page_listing_buttons")
def page_listing_buttons(page, page_perms, is_parent=False, next_url=None):
    yield wagtailadmin_widgets.PageListingButton(
        "Import Content", reverse("import"), priority=10
    )


@hooks.register("register_reports_menu_item")
def register_stale_content_report_menu_item():
    return AdminOnlyMenuItem(
        "Stale Content",
        reverse("stale_content_report"),
        classname="icon icon-" + ContentPageReportView.header_icon,
        order=700,
    )


@hooks.register("register_admin_urls")
def register_stale_content_report_url():
    return [
        path(
            "reports/stale-content/",
            ContentPageReportView.as_view(),
            name="stale_content_report",
        ),
    ]


@hooks.register("register_reports_menu_item")
def register_page_views_report_menu_item():
    return AdminOnlyMenuItem(
        "Page Views",
        reverse("page_view_report"),
        classname="icon icon-doc-empty",
        order=700,
    )


@hooks.register("register_admin_urls")
def register_page_views_report_url():
    return [
        path(
            "reports/page-views/",
            PageViewReportView.as_view(),
            name="page_view_report",
        ),
    ]


class ContentPageAdmin(ModelAdmin):
    body_truncate_size = 200
    model = ContentPage
    menu_label = "ContentPages"
    menu_icon = "pilcrow"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    index_view_class = CustomIndexView
    list_display = (
        "slug",
        "title",
        "web_body",
        "subtitle",
        "wa_body",
        "sms_body",
        "ussd_body",
        "mess_body",
        "vib_body",
        "replies",
        "trigger",
        "tag",
        "related_pages",
        "parental",
    )

    search_fields = (
        "title",
        "body",
        "whatsapp_body",
        "sms_body",
        "ussd_body",
        "messenger_body",
        "viber_body",
        "slug",
    )
    list_export = "title"

    def replies(self, obj):
        return list(obj.quick_replies.all())

    replies.short_description = "Quick Replies"

    def trigger(self, obj):
        return list(obj.triggers.all())

    trigger.short_description = "Triggers"

    def tag(self, obj):
        return list(obj.tags.all())

    tag.short_description = "Tags"

    def wa_body(self, obj):
        body = "\n".join(m.value["message"] for m in obj.whatsapp_body)
        return truncatechars(str(body), self.body_truncate_size)

    wa_body.short_description = "Whatsapp Body"

    def sms_body(self, obj):
        body = "\n".join(m.value["message"] for m in obj.sms_body)
        return truncatechars(str(body), self.body_truncate_size)

    sms_body.short_description = "SMS Body"

    def ussd_body(self, obj):
        body = "\n".join(m.value["message"] for m in obj.ussd_body)
        return truncatechars(str(body), self.body_truncate_size)

    ussd_body.short_description = "USSD Body"

    def mess_body(self, obj):
        body = "\n".join(m.value["message"] for m in obj.messenger_body)
        return truncatechars(str(body), self.body_truncate_size)

    mess_body.short_description = "Messenger Body"

    def vib_body(self, obj):
        body = "\n".join(m.value["message"] for m in obj.viber_body)
        return truncatechars(str(body), self.body_truncate_size)

    vib_body.short_description = "Viber Body"

    def web_body(self, obj):
        return truncatechars(str(obj.body), self.body_truncate_size)

    web_body.short_description = "Web Body"

    def parental(self, obj):
        return obj.get_parent()

    parental.short_description = "Parent"


class OrderedContentSetViewSet(SnippetViewSet):
    model = OrderedContentSet
    icon = "order"
    menu_order = 200
    add_to_admin_menu = True
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("name", "latest_draft_profile_fields", "num_pages", "status")
    list_export = (
        "name",
        "profile_field",
        "page",
        "time",
        "unit",
        "before_or_after",
        "contact_field",
    )
    search_fields = ("name", "profile_fields")


class WhatsAppTemplateViewSet(SnippetViewSet):
    model = WhatsAppTemplate
    body_truncate_size = 200
    icon = "order"
    menu_order = 200
    add_to_admin_menu = True
    add_to_settings_menu = False
    exclude_from_explorer = False
    # menu_label = "WhatsAppTemplates"
    # menu_icon = "pilcrow"
    # menu_order = 200
    # add_to_settings_menu = False
    # exclude_from_explorer = False
    # index_view_class = CustomIndexView
    list_display = (
        "name",
        "category",
        "body",
        "locale",
        "status",
        "quick_replies",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("category"),
                FieldPanel("message"),
                FieldPanel("quick_replies", heading="Quick Replies"),
                FieldPanel("locale"),
            ],
            heading="Whatsapp Template",
        ),
    ]

    search_fields = (
        "name",
        "category",
        "message",
        "locale",
    )


register_snippet(OrderedContentSetViewSet)
modeladmin_register(ContentPageAdmin)
register_snippet(WhatsAppTemplateViewSet)
