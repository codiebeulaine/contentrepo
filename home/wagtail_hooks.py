from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin import widgets as wagtailadmin_widgets
from wagtail.admin.menu import AdminOnlyMenuItem
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TitleFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Assessment, ContentPage, OrderedContentSet, WhatsAppTemplate

from .views import (  # isort:skip
    ContentPageReportView,
    CustomIndexView,
    CustomIndexViewAssessment,
    OrderedContentSetUploadView,
    PageViewReportView,
    ContentUploadView,
    AssessmentUploadView,
    CustomIndexViewWhatsAppTemplate,
    WhatsAppTemplateUploadView,
)


@hooks.register("before_delete_page")
def prevent_deletion_if_linked(request, page):
    """
    Check if the page is a ContentPage and if it has any links to prevent
    the deletion of a page if it is linked to other content.
    """
    if page.content_type.name != ContentPage._meta.verbose_name:
        return
    page_links, orderedcontentset_links, wat_links = page.get_all_links()

    if page_links or orderedcontentset_links:
        msg_parts = ["You can't delete this page while it is linked."]

        if page_links:
            msg_parts.append("<br>Content Pages:")
            for link in page_links:
                msg_parts.append(f'<a href="{link[0]}">{link[1]}</a>')

        if orderedcontentset_links:
            msg_parts.append("<br>Ordered Content Sets:")
            for link in orderedcontentset_links:
                msg_parts.append(f'<a href="{link[0]}">{link[1]}</a>')

        messages.warning(request, "<br>".join(msg_parts))
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))


@hooks.register("register_admin_urls")
def get_import_urls():
    """
    Define additional admin URLs for various content import views.
    """
    return [
        path("import/", ContentUploadView.as_view(), name="import"),
        path(
            "import_orderedcontentset/",
            OrderedContentSetUploadView.as_view(),
            name="import_orderedcontentset",
        ),
        path(
            "import_assessment/",
            AssessmentUploadView.as_view(),
            name="import_assessment",
        ),
        path(
            "import_whatsapptemplate/",
            WhatsAppTemplateUploadView.as_view(),
            name="import_whatsapptemplate",
        ),
    ]


@hooks.register("register_page_listing_buttons")
def get_import_content_button(page, page_perms, is_parent=False, next_url=None):
    """
    Generate buttons to add to action list for importing content.
    """
    yield wagtailadmin_widgets.PageListingButton(
        "Import Content", reverse("import"), priority=10
    )


@hooks.register("register_reports_menu_item")
def get_stale_content_report_menu_item():
    """
    Create a admin only sub menu item for the Stale Content report.
    """
    return AdminOnlyMenuItem(
        "Stale Content",
        reverse("stale_content_report"),
        classname="icon icon-" + ContentPageReportView.header_icon,
        order=700,
    )


@hooks.register("register_admin_urls")
def get_stale_content_report_url():
    """
    Create additional URL for the State Content Report.
    """
    return [
        path(
            "reports/stale-content/",
            ContentPageReportView.as_view(),
            name="stale_content_report",
        ),
    ]


@hooks.register("register_reports_menu_item")
def get_page_views_report_menu_item():
    """
    Create a admin only sub menu item for the Page Views report.
    """
    return AdminOnlyMenuItem(
        "Page Views",
        reverse("page_view_report"),
        classname="icon icon-doc-empty",
        order=700,
    )


@hooks.register("register_admin_urls")
def get_page_views_report_url():
    """
    Create additional URL for the Page Views report.
    """
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
    list_filter = ("locale",)

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
    list_export = ("locale", "title")


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
        "slug",
        "language_code",
    )

    export_headings = {"language_code": "Locale"}

    list_filter = ("locale",)
    search_fields = ("name", "profile_fields")


class WhatsAppTemplateAdmin(SnippetViewSet):
    model = WhatsAppTemplate
    body_truncate_size = 200
    icon = "order"
    menu_order = 200
    add_to_admin_menu = True
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_export = "name"
    list_display = (
        "name",
        "get_category_display",
        "locale",
        "status",
        "get_submission_status_display",
    )

    list_filter = ("locale",)

    search_fields = (
        "name",
        "category",
        "message",
        "locale",
    )

    index_view_class = CustomIndexViewWhatsAppTemplate

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("category"),
                FieldPanel("image"),
                FieldPanel("message"),
                FieldPanel("quick_replies", heading="Quick Replies"),
                FieldPanel("locale"),
                FieldPanel("example_values"),
                FieldPanel("submission_name", read_only=True),
                FieldPanel("submission_status", read_only=True),
                FieldPanel("submission_result", read_only=True),
            ],
            heading="Whatsapp Template",
        ),
    ]


class AssessmentAdmin(SnippetViewSet):
    menu_label = "CMS Forms"
    model = Assessment
    add_to_admin_menu = True
    list_display = ("title", "slug", "version", "locale")
    search_fields = ("title", "slug", "version")
    list_filter = ("locale",)
    icon = "circle-check"
    menu_order = 300
    list_export = "title"
    index_view_class = CustomIndexViewAssessment

    panels = [
        MultiFieldPanel(
            [
                TitleFieldPanel("title"),
                FieldPanel("slug", widget=SlugInput()),
                FieldPanel("version"),
                FieldPanel("locale"),
                FieldPanel("tags"),
            ],
            heading="Identifiers",
        ),
        MultiFieldPanel(
            [
                FieldPanel("high_result_page"),
                FieldPanel("high_inflection"),
                FieldPanel("medium_result_page"),
                FieldPanel("medium_inflection"),
                FieldPanel("low_result_page"),
                FieldPanel("skip_threshold"),
                FieldPanel("skip_high_result_page"),
            ],
            heading="Results",
        ),
        MultiFieldPanel(
            [
                FieldPanel("generic_error"),
                FieldPanel("questions"),
            ],
            heading="Questions",
        ),
    ]


# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(ContentPageAdmin)
register_snippet(AssessmentAdmin)
register_snippet(OrderedContentSetViewSet)
# Flag for turning on Standalone Whatsapp Templates, still in development
if settings.ENABLE_STANDALONE_WHATSAPP_TEMPLATES:
    register_snippet(WhatsAppTemplateAdmin)
