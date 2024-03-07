import json
import queue
from pathlib import Path

import pytest
from wagtail import blocks
from wagtail.models.sites import Site  # type: ignore

from home.content_import_export import import_content
from home.models import (
    AnswerBlock,
    Assessment,
    ContentPage,
    HomePage,
    OrderedContentSet,
    PageView,
    QuestionBlock,
    VariationBlock,
)

from .page_builder import (
    MBlk,
    MBody,
    PageBuilder,
    SBlk,
    SBody,
    UBlk,
    UBody,
    WABlk,
    WABody,
)
from .utils import create_page


@pytest.fixture()
def uclient(client, django_user_model):
    creds = {"username": "test", "password": "test"}
    django_user_model.objects.create_user(**creds)
    client.login(**creds)
    return client


@pytest.mark.django_db
class TestContentPageAPI:
    @pytest.fixture(autouse=True)
    def create_test_data(self):
        """
        Create the content that all the tests in this class will use.
        """
        home_page = HomePage.objects.first()
        main_menu = PageBuilder.build_cpi(home_page, "main-menu", "Main Menu")
        content_page1 = PageBuilder.build_cp(
            parent=main_menu,
            slug="main-menu-first-time-user",
            title="main menu first time user",
            bodies=[
                WABody(
                    "main menu first time user", [WABlk("*Welcome to HealthAlert* 🌍")]
                ),
                MBody(
                    "main menu first time user", [MBlk("*Welcome to HealthAlert* 🌍")]
                ),
                SBody("main menu first time user", [SBlk("*Welcome to HealthAlert*")]),
                UBody("main menu first time user", [UBlk("*Welcome to HealthAlert*")]),
            ],
            tags=["menu"],
            quick_replies=["Self-help", "Settings", "Health Info"],
            triggers=["Main menu"],
        )
        PageBuilder.build_cp(
            parent=content_page1,
            slug="health-info",
            title="health info",
            bodies=[
                WABody("health info", [WABlk("*Health information* 🏥")]),
                MBody("health info", [MBlk("*Health information* 🏥")]),
                SBody("health info", [SBlk("*Health information* ")]),
                UBody("health info", [UBlk("*Health information* ")]),
            ],
            tags=["health_info"],
        )
        PageBuilder.build_cp(
            parent=content_page1,
            slug="self-help",
            title="self-help",
            bodies=[
                WABody("self-help", [WABlk("*Self-help programs* 🌬️")]),
                MBody("self-help", [MBlk("*Self-help programs* 🌬️")]),
                SBody("self-help", [SBlk("*Self-help programs*")]),
                UBody("self-help", [UBlk("*Self-help programs*")]),
            ],
            tags=["self_help"],
        )

    def test_login_required(self, client):
        """
        Users that aren't logged in shouldn't be allowed to access the API
        """
        response = client.get("/api/v2/pages/?tag=menu")
        assert response.status_code == 401

    def test_tag_filtering(self, uclient):
        """
        If a tag filter is provided, only pages with matching tags are returned.
        """
        # it should return 1 page for correct tag
        response = uclient.get("/api/v2/pages/?tag=menu")
        content = json.loads(response.content)
        assert content["count"] == 1
        # it should return 1 page for Uppercase tag
        response = uclient.get("/api/v2/pages/?tag=Menu")
        content = json.loads(response.content)
        assert content["count"] == 1
        # it should not return any pages for bogus tag
        response = uclient.get("/api/v2/pages/?tag=bogus")
        content = json.loads(response.content)
        assert content["count"] == 0
        # it should return all pages for no tag
        response = uclient.get("/api/v2/pages/")
        content = json.loads(response.content)
        # exclude home pages and index pages
        assert content["count"] == 3
        # it should not return pages with tags in the draft
        create_page(tags=["Menu"]).unpublish()
        response = uclient.get("/api/v2/pages/?tag=Menu")
        content = json.loads(response.content)
        assert content["count"] == 1
        # If QA flag is sent then it should return pages with tags in the draft
        response = uclient.get("/api/v2/pages/?tag=Menu&qa=True")
        content = json.loads(response.content)
        assert content["count"] == 2

    def test_whatsapp_draft(self, uclient):
        """
        Unpublished whatsapp pages are returned if the qa param is set.
        """
        page2 = ContentPage.objects.last()
        page2.unpublish()
        page_id = page2.id
        url = f"/api/v2/pages/{page_id}/?whatsapp=True&qa=True"
        # it should return specific page that is in draft
        response = uclient.get(url)
        content = json.loads(response.content)
        message = "*Self-help programs* 🌬️"
        # the page is not live but whatsapp content is returned
        assert not page2.live
        assert content["body"]["text"]["value"]["message"].replace("\r", "") == message

    def test_messenger_draft(self, uclient):
        """
        Unpublished messenger pages are returned if the qa param is set.
        """
        page2 = ContentPage.objects.last()
        page2.unpublish()
        page_id = page2.id
        url = f"/api/v2/pages/{page_id}/?messenger=True&qa=True"
        # it should return specific page that is in draft
        response = uclient.get(url)

        message = "*Self-help programs* 🌬️"
        content = json.loads(response.content)

        # the page is not live but messenger content is returned
        assert not page2.live
        assert content["body"]["text"]["message"].replace("\r", "") == message

    def test_pagination(self, uclient):
        """
        FIXME:
         * It's unclear what this is actually testing.
         * Should it be multiple tests instead of just one?
        """
        page1 = ContentPage.objects.first()

        # it should not return the web body if enable_whatsapp=false
        page1.enable_whatsapp = False
        page1.save_revision().publish()
        response = uclient.get(f"/api/v2/pages/{page1.id}/?whatsapp=True")

        content = response.content
        assert content == b""

        # it should only return the whatsapp body if enable_whatsapp=True
        page1.enable_whatsapp = True
        page1.save_revision().publish()

        # it should only return the first paragraph if no specific message
        # is requested
        response = uclient.get(f"/api/v2/pages/{page1.id}/?whatsapp=True")
        content = json.loads(response.content)
        assert content["body"]["message"] == 1
        assert content["body"]["previous_message"] is None
        assert content["body"]["total_messages"] == 1
        assert content["body"]["revision"] == page1.get_latest_revision().id
        assert "*Welcome to HealthAlert*" in content["body"]["text"]["value"]["message"]

        # it should return an appropriate error if requested message index
        # is out of range
        response = uclient.get(f"/api/v2/pages/{page1.id}/?whatsapp=True&message=3")
        content = json.loads(response.content)
        assert response.status_code == 400
        assert content == ["The requested message does not exist"]

        # it should return an appropriate error if requested message is not
        # a positive integer value
        response = uclient.get(
            f"/api/v2/pages/{page1.id}/?whatsapp=True&message=notint"
        )
        content = json.loads(response.content)
        assert response.status_code == 400
        assert content == [
            "Please insert a positive integer for message in the query string"
        ]

        body = []
        for i in range(15):
            block = blocks.StructBlock(
                [
                    ("message", blocks.TextBlock()),
                    ("variation_messages", blocks.ListBlock(VariationBlock())),
                ]
            )
            block_value = block.to_python(
                {"message": f"WA Message {i+1}", "variation_messages": []}
            )
            body.append(("Whatsapp_Message", block_value))

        page1.whatsapp_body = body
        page1.save_revision().publish()

        # it should only return the 11th paragraph if 11th message
        # is requested
        response = uclient.get(f"/api/v2/pages/{page1.id}/?whatsapp=True&message=11")
        content = json.loads(response.content)
        assert content["body"]["message"] == 11
        assert content["body"]["next_message"] == 12
        assert content["body"]["previous_message"] == 10
        assert content["body"]["text"]["value"]["message"] == "WA Message 11"

    def test_number_of_queries(self, uclient, django_assert_num_queries):
        """
        Make sure we aren't making an enormous number of queries.

        FIXME:
         * Should we document what these queries actually are?
        """
        # Run this once without counting, because there are two queries at the
        # end that only happen if this is the first test that runs.
        uclient.get("/api/v2/pages/")
        with django_assert_num_queries(8):
            uclient.get("/api/v2/pages/")

    def test_detail_view_content(self, uclient):
        """
        Fetching the detail view of a page returns the page content.
        """
        page2 = ContentPage.objects.last()
        response = uclient.get(f"/api/v2/pages/{page2.id}/")
        content = response.json()

        # There's a lot of metadata, so only check selected fields.
        meta = content.pop("meta")
        assert meta["type"] == "home.ContentPage"
        assert meta["slug"] == page2.slug
        assert meta["parent"]["id"] == page2.get_parent().id
        assert meta["locale"] == "en"

        assert content == {
            "id": page2.id,
            "title": "self-help",
            "subtitle": "",
            "body": {"text": []},
            "tags": ["self_help"],
            "triggers": [],
            "quick_replies": [],
            "related_pages": [],
            "has_children": False,
        }

    def test_detail_view_increments_count(self, uclient):
        """
        Fetching the detail view of a page increments the view count.
        """
        page2 = ContentPage.objects.last()
        assert PageView.objects.count() == 0

        uclient.get(f"/api/v2/pages/{page2.id}/")
        assert PageView.objects.count() == 1
        view = PageView.objects.last()
        assert view.message is None

        uclient.get(f"/api/v2/pages/{page2.id}/")
        uclient.get(f"/api/v2/pages/{page2.id}/")
        assert PageView.objects.count() == 3
        view = PageView.objects.last()
        assert view.message is None

    def test_detail_view_with_children(self, uclient):
        """
        Fetching the detail view of a page with children indicates that the
        page has children.
        """
        page1 = ContentPage.objects.first()
        response = uclient.get(f"/api/v2/pages/{page1.id}/")
        content = response.json()

        # There's a lot of metadata, so only check selected fields.
        meta = content.pop("meta")
        assert meta["type"] == "home.ContentPage"
        assert meta["slug"] == page1.slug
        assert meta["parent"]["id"] == page1.get_parent().id
        assert meta["locale"] == "en"

        assert content == {
            "id": page1.id,
            "title": "main menu first time user",
            "subtitle": "",
            "body": {"text": []},
            "tags": ["menu"],
            "triggers": ["Main menu"],
            "quick_replies": ["Health Info", "Self-help", "Settings"],
            "related_pages": [],
            "has_children": True,
        }

    def test_detail_view_whatsapp_message(self, uclient):
        """
        Fetching a detail page and selecting the WhatsApp content returns the
        first WhatsApp message in the body.
        """
        page1 = ContentPage.objects.first()
        response = uclient.get(f"/api/v2/pages/{page1.id}/?whatsapp=true")
        content = response.json()

        # There's a lot of metadata, so only check selected fields.
        meta = content.pop("meta")
        assert meta["type"] == "home.ContentPage"
        assert meta["slug"] == page1.slug
        assert meta["parent"]["id"] == page1.get_parent().id
        assert meta["locale"] == "en"

        assert content["id"] == page1.id
        assert content["title"] == "main menu first time user"

        # There's a lot of body, so only check selected fields.
        body = content.pop("body")
        assert body["message"] == 1
        assert body["next_message"] is None
        assert body["previous_message"] is None
        assert body["total_messages"] == 1
        assert body["text"]["type"] == "Whatsapp_Message"
        assert body["text"]["value"]["message"] == "*Welcome to HealthAlert* 🌍"

    def test_detail_view_no_content_page(self, uclient):
        """
        We get a validation error if we request a page that doesn't exist.

        FIXME:
         * Is 400 (ValidationError) really an appropriate response code for
           this? 404 seems like a better fit for failing to find a page we're
           looking up by id.
        """
        # it should return the validation error for content page that doesn't exist
        response = uclient.get("/api/v2/pages/1/")
        assert response.status_code == 400

        content = response.json()
        assert content == {"page": ["Page matching query does not exist."]}
        assert content.get("page") == ["Page matching query does not exist."]


@pytest.mark.django_db
class TestWhatsAppMessages:
    """
    FIXME:
     * Should some of the WhatsApp tests from TestPagination live here instead?
    """

    def test_whatsapp_detail_view_with_button(self, uclient):
        """
        Next page buttons in WhatsApp messages are present in the message body.
        """
        page = ContentPage(
            title="test",
            slug="text",
            enable_whatsapp=True,
            whatsapp_body=[
                {
                    "type": "Whatsapp_Message",
                    "value": {
                        "message": "test message",
                        "buttons": [
                            {"type": "next_message", "value": {"title": "Tell me more"}}
                        ],
                    },
                }
            ],
        )
        homepage = HomePage.objects.first()
        homepage.add_child(instance=page)
        page.save_revision().publish()

        response = uclient.get(f"/api/v2/pages/{page.id}/?whatsapp=true&message=1")
        content = response.json()
        [button] = content["body"]["text"]["value"]["buttons"]
        button.pop("id")
        assert button == {"type": "next_message", "value": {"title": "Tell me more"}}

    def test_whatsapp_template(self, uclient):
        """
        FIXME:
         * Is this actually a template message?
        """
        page = ContentPage(
            title="test",
            slug="text",
            enable_whatsapp=True,
            whatsapp_body=[
                {
                    "type": "Whatsapp_Message",
                    "value": {
                        "message": "test message",
                        "buttons": [
                            {"type": "next_message", "value": {"title": "Tell me more"}}
                        ],
                    },
                }
            ],
            whatsapp_template_category="MARKETING",
        )
        homepage = HomePage.objects.first()
        homepage.add_child(instance=page)
        page.save_revision().publish()

        response = uclient.get(f"/api/v2/pages/{page.id}/?whatsapp=true&message=1")
        content = response.json()
        body = content["body"]
        assert body["whatsapp_template_category"] == "MARKETING"

    def test_whatsapp_body(self, uclient):
        """
        Should have the WhatsApp specific fields included in the body; if it's a
        template, what's the template name, the text body of the message.
        """
        page = create_page(
            is_whatsapp_template=True, whatsapp_template_name="test_template"
        )

        # it should return the correct details
        response = uclient.get(f"/api/v2/pages/{page.id}/?whatsapp")
        content = response.json()
        assert content["body"]["is_whatsapp_template"]
        assert content["body"]["whatsapp_template_name"] == "test_template"
        assert content["body"]["text"]["value"]["message"] == "Test WhatsApp Message 1"

    def test_whatsapp_detail_view_with_variations(self, uclient):
        """
        Variation blocks in WhatsApp messages are present in the message body.
        """
        # variations should be in the whatsapp content
        page = create_page(tags=["tag1", "tag2"], add_variation=True)

        response = uclient.get(f"/api/v2/pages/{page.id}/?whatsapp=true&message=1")
        content = response.json()

        var_content = content["body"]["text"]["value"]["variation_messages"]
        assert len(var_content) == 1
        assert var_content[0]["profile_field"] == "gender"
        assert var_content[0]["value"] == "female"
        assert var_content[0]["message"] == "Test Title - female variation"

        assert PageView.objects.count() == 1
        view = PageView.objects.last()
        assert view.message == 1


@pytest.mark.django_db
class TestOrderedContentSetAPI:
    @pytest.fixture(autouse=True)
    def create_test_data(self):
        """
        Create the content that all the tests in this class will use.
        """
        path = Path("home/tests/content2.csv")
        with path.open(mode="rb") as f:
            import_content(f, "CSV", queue.Queue())
        self.page1 = ContentPage.objects.first()
        self.ordered_content_set = OrderedContentSet(name="Test set")
        self.ordered_content_set.pages.append(("pages", {"contentpage": self.page1}))
        self.ordered_content_set.profile_fields.append(("gender", "female"))
        self.ordered_content_set.save()

        self.ordered_content_set_timed = OrderedContentSet(name="Test set")
        self.ordered_content_set_timed.pages.append(
            (
                "pages",
                {
                    "contentpage": self.page1,
                    "time": 5,
                    "unit": "Days",
                    "before_or_after": "Before",
                    "contact_field": "EDD",
                },
            )
        )

        self.ordered_content_set_timed.profile_fields.append(("gender", "female"))
        self.ordered_content_set_timed.save()

    def test_orderedcontent_endpoint(self, uclient):
        """
        The orderedcontent endpoint returns a list of ordered sets, including
        name and profile fields.
        """
        # it should return a list of ordered sets and show the profile fields
        response = uclient.get("/api/v2/orderedcontent/")
        content = json.loads(response.content)
        assert content["count"] == 2
        assert content["results"][0]["name"] == self.ordered_content_set.name
        assert content["results"][0]["profile_fields"][0] == {
            "profile_field": "gender",
            "value": "female",
        }

    def test_orderedcontent_detail_endpoint(self, uclient):
        """
        The orderedcontent detail page lists the pages that are part of the
        ordered set.
        """
        # it should return the list of pages that are part of the ordered content set
        response = uclient.get(f"/api/v2/orderedcontent/{self.ordered_content_set.id}/")
        content = json.loads(response.content)
        assert content["name"] == self.ordered_content_set.name
        assert content["profile_fields"][0] == {
            "profile_field": "gender",
            "value": "female",
        }
        assert content["pages"][0] == {
            "id": self.page1.id,
            "title": self.page1.title,
            "time": None,
            "unit": None,
            "before_or_after": None,
            "contact_field": None,
        }

    def test_orderedcontent_detail_endpoint_timed(self, uclient):
        """
        The orderedcontent detail page lists the pages that are part of the
        ordered set, including information about timing.
        """
        # it should return the list of pages that are part of the ordered content set
        response = uclient.get(
            f"/api/v2/orderedcontent/{self.ordered_content_set_timed.id}/"
        )
        content = json.loads(response.content)
        assert content["name"] == self.ordered_content_set_timed.name
        assert content["profile_fields"][0] == {
            "profile_field": "gender",
            "value": "female",
        }
        assert content["pages"][0] == {
            "id": self.page1.id,
            "title": self.page1.title,
            "time": 5,
            "unit": "Days",
            "before_or_after": "Before",
            "contact_field": "EDD",
        }

    def test_orderedcontent_detail_endpoint_rel_pages_flag(self, uclient):
        """
        The orderedcontent detail page lists the pages that are part of the
        ordered set, including related pages.
        """
        rel_page = create_page("Related Page")
        self.page1.related_pages = [{"type": "related_page", "value": rel_page.id}]
        self.page1.save_revision().publish()

        # it should return the list of pages that are part of the ordered content set
        response = uclient.get(
            f"/api/v2/orderedcontent/{self.ordered_content_set.id}/?show_related=true"
        )
        content = json.loads(response.content)
        assert content["name"] == self.ordered_content_set.name
        assert content["profile_fields"][0] == {
            "profile_field": "gender",
            "value": "female",
        }
        assert content["pages"][0] == {
            "id": self.page1.id,
            "title": self.page1.title,
            "time": None,
            "unit": None,
            "before_or_after": None,
            "contact_field": None,
            "related_pages": [rel_page.id],
        }

    def test_orderedcontent_detail_endpoint_tags_flag(self, uclient):
        """
        The orderedcontent detail page lists the pages that are part of the
        ordered set, including tags.
        """
        # it should return the list of pages that are part of the ordered content set
        response = uclient.get(
            f"/api/v2/orderedcontent/{self.ordered_content_set.id}/?show_tags=true"
        )
        content = json.loads(response.content)
        assert content["name"] == self.ordered_content_set.name
        assert content["profile_fields"][0] == {
            "profile_field": "gender",
            "value": "female",
        }
        assert content["pages"][0]["tags"] == [t.name for t in self.page1.tags.all()]


@pytest.mark.django_db
class TestContentPageAPI2:
    """
    Tests contentpage API without test data fixtures
    """

    def test_platform_filtering(self, uclient):
        """
        If a platform filter is provided, only pages with content for that
        platform are returned.
        """
        home_page = HomePage.objects.first()
        main_menu = PageBuilder.build_cpi(home_page, "main-menu", "Main Menu")
        PageBuilder.build_cp(
            parent=main_menu,
            slug="main-menu-first-time-user",
            title="main menu first time user",
            bodies=[],
            web_body=["Colour"],
        )
        PageBuilder.build_cp(
            parent=main_menu,
            slug="health-info",
            title="health info",
            bodies=[
                WABody("health info", [WABlk("*Health information* 🏥")]),
            ],
        )
        PageBuilder.build_cp(
            parent=main_menu,
            slug="self-help",
            title="self-help",
            bodies=[
                MBody("self-help", [MBlk("*Self-help programs* 🌬️")]),
            ],
        )
        PageBuilder.build_cp(
            parent=main_menu,
            slug="self-help-sms",
            title="self-help-sms",
            bodies=[
                SBody("self-help-sms", [SBlk("*Self-help programs*SMS")]),
            ],
        )
        PageBuilder.build_cp(
            parent=main_menu,
            slug="self-help-ussd",
            title="self-help-ussd",
            bodies=[
                UBody("self-help-ussd", [UBlk("*Self-help programs* USSD")]),
            ],
        )

        # it should return only web pages if filtered
        response = uclient.get("/api/v2/pages/?web=true")
        content = json.loads(response.content)
        assert content["count"] == 1
        # it should return only whatsapp pages if filtered
        response = uclient.get("/api/v2/pages/?whatsapp=true")
        content = json.loads(response.content)
        assert content["count"] == 1
        # it should return only sms pages if filtered
        response = uclient.get("/api/v2/pages/?sms=true")
        content = json.loads(response.content)
        assert content["count"] == 1
        # it should return only ussd pages if filtered
        response = uclient.get("/api/v2/pages/?ussd=true")
        content = json.loads(response.content)
        assert content["count"] == 1
        # it should return only messenger pages if filtered
        response = uclient.get("/api/v2/pages/?messenger=true")
        content = json.loads(response.content)
        assert content["count"] == 1
        # it should return only viber pages if filtered
        response = uclient.get("/api/v2/pages/?viber=true")
        content = json.loads(response.content)
        assert content["count"] == 0
        # it should return all pages for no filter
        response = uclient.get("/api/v2/pages/")
        content = json.loads(response.content)
        # exclude home pages and index pages
        assert content["count"] == 5

    def test_ussd_content(self, uclient):
        """
        If a ussd query param is provided, only pages with content for that
        platform are returned.
        """
        home_page = HomePage.objects.first()
        main_menu = PageBuilder.build_cpi(home_page, "main-menu", "Main Menu")
        PageBuilder.build_cp(
            parent=main_menu,
            slug="main-menu-first-time-user",
            title="main menu first time user",
            bodies=[],
            web_body=["Colour"],
        )
        PageBuilder.build_cp(
            parent=main_menu,
            slug="health-info",
            title="health info",
            bodies=[
                UBody("health info", [UBlk("*Health information* U")]),
            ],
        )

        # it should return only USSD pages if filtered
        response = uclient.get("/api/v2/pages/?ussd=true")
        content = json.loads(response.content)
        assert content["count"] == 1

    def test_sms_content(self, uclient):
        """
        If a sms query param is provided, only pages with content for that
        platform are returned.
        """
        home_page = HomePage.objects.first()
        main_menu = PageBuilder.build_cpi(home_page, "main-menu", "Main Menu")
        PageBuilder.build_cp(
            parent=main_menu,
            slug="main-menu-first-time-user",
            title="main menu first time user",
            bodies=[],
            web_body=["Colour"],
        )
        PageBuilder.build_cp(
            parent=main_menu,
            slug="health-info",
            title="health info",
            bodies=[
                SBody("health info", [SBlk("*Health information* S")]),
            ],
        )

        # it should return only USSD pages if filtered
        response = uclient.get("/api/v2/pages/?sms=true")
        content = json.loads(response.content)
        assert content["count"] == 1


@pytest.mark.django_db
class TestAssessmentAPI:
    @pytest.fixture(autouse=True)
    def create_test_data(self):
        """
        Create the content that all the tests in this class will use.
        """
        self.assessment = Assessment(title="Test Assessment", slug="test-assessment")
        self.high_result_page = ContentPage(
            title="high result",
            slug="high-result",
            enable_whatsapp=True,
            whatsapp_body=[
                {
                    "type": "Whatsapp_Message",
                    "value": {
                        "message": "test message",
                        "buttons": [
                            {"type": "next_message", "value": {"title": "Tell me more"}}
                        ],
                    },
                }
            ],
        )
        self.medium_result_page = ContentPage(
            title="medium result",
            slug="medium-result",
            enable_whatsapp=True,
            whatsapp_body=[
                {
                    "type": "Whatsapp_Message",
                    "value": {
                        "message": "test message",
                        "buttons": [
                            {"type": "next_message", "value": {"title": "Tell me more"}}
                        ],
                    },
                }
            ],
        )
        self.low_result_page = ContentPage(
            title="low result",
            slug="low-result",
            enable_whatsapp=True,
            whatsapp_body=[
                {
                    "type": "Whatsapp_Message",
                    "value": {
                        "message": "test message",
                        "buttons": [
                            {"type": "next_message", "value": {"title": "Tell me more"}}
                        ],
                    },
                }
            ],
        )
        homepage = HomePage.objects.first()
        homepage.add_child(instance=self.high_result_page)
        homepage.add_child(instance=self.medium_result_page)
        homepage.add_child(instance=self.low_result_page)
        self.high_result_page.save_revision().publish()
        self.medium_result_page.save_revision().publish()
        self.low_result_page.save_revision().publish()
        site = Site.objects.get(is_default_site=True)
        self.assessment.locale = site.root_page.locale
        self.assessment.high_result_page = self.high_result_page
        self.assessment.high_inflection = 5.0
        self.assessment.medium_result_page = self.medium_result_page
        self.assessment.medium_inflection = 2.0
        self.assessment.low_result_page = self.low_result_page
        self.assessment.generic_error = "This is a generic error"
        answers_block = blocks.ListBlock(AnswerBlock())
        answers_block_value = answers_block.to_python(
            [
                {"answer": "Crunchie", "score": "5"},
                {"answer": "Flake", "score": "3"},
            ]
        )
        question_block = QuestionBlock()
        question_block_value = question_block.to_python(
            {
                "question": "What is the best chocolate?",
                "error": "Invalid answer",
                "answers": answers_block_value,
            }
        )
        self.assessment.questions.append(
            (
                "question",
                question_block_value,
            )
        )
        self.assessment.save()

    def test_assessment_endpoint(self, uclient):
        response = uclient.get("/api/v2/assessment/")
        content = json.loads(response.content)
        assert content["count"] == 1
        assert content["results"][0]["title"] == self.assessment.title
        assert content["results"][0]["high_result_page"] == {
            "id": self.high_result_page.id,
            "title": self.high_result_page.title,
        }
        assert content["results"][0]["high_inflection"] == 5.0
        assert content["results"][0]["medium_result_page"] == {
            "id": self.medium_result_page.id,
            "title": self.medium_result_page.title,
        }
        assert content["results"][0]["medium_inflection"] == 2.0
        assert content["results"][0]["low_result_page"] == {
            "id": self.low_result_page.id,
            "title": self.low_result_page.title,
        }

    def test_assessment_detail_endpoint(self, uclient):
        response = uclient.get(f"/api/v2/assessment/{self.assessment.id}/")
        content = json.loads(response.content)
        assert content["title"] == self.assessment.title
        assert content["high_result_page"] == {
            "id": self.high_result_page.id,
            "title": self.high_result_page.title,
        }
        assert content["high_inflection"] == 5.0
        assert content["medium_result_page"] == {
            "id": self.medium_result_page.id,
            "title": self.medium_result_page.title,
        }
        assert content["medium_inflection"] == 2.0
        assert content["low_result_page"] == {
            "id": self.low_result_page.id,
            "title": self.low_result_page.title,
        }

    def test_assessment_endpoint_with_drafts(self, uclient):
        """
        Unpublished assessments are returned if the qa param is set.
        """
        self.assessment.unpublish()
        url = "/api/v2/assessment/?qa=True"
        # it should return a list of assessments with the unpublished one included
        response = uclient.get(url)
        content = json.loads(response.content)

        # the assessment is not live but content is returned
        assert not self.assessment.live
        assert content["count"] == 1
        assert content["results"][0]["title"] == self.assessment.title
        assert content["results"][0]["high_result_page"] == {
            "id": self.high_result_page.id,
            "title": self.high_result_page.title,
        }
        assert content["results"][0]["high_inflection"] == 5.0
        assert content["results"][0]["medium_result_page"] == {
            "id": self.medium_result_page.id,
            "title": self.medium_result_page.title,
        }
        assert content["results"][0]["medium_inflection"] == 2.0
        assert content["results"][0]["low_result_page"] == {
            "id": self.low_result_page.id,
            "title": self.low_result_page.title,
        }

    def test_assessment_endpoint_without_drafts(self, uclient):
        """
        Unpublished assessments are not returned if the qa param is not set.
        """
        self.assessment.unpublish()
        url = "/api/v2/assessment/"
        # it should return nothing
        response = uclient.get(url)
        content = json.loads(response.content)

        # the assessment is not live
        assert not self.assessment.live
        assert content["count"] == 0

    def test_assessment_detail_endpoint_with_drafts(self, uclient):
        """
        Unpublished assessments are returned if the qa param is set.
        """
        self.assessment.unpublish()
        url = f"/api/v2/assessment/{self.assessment.id}/?qa=True"
        # it should return specific assessment that is in draft
        response = uclient.get(url)
        content = json.loads(response.content)

        # the assessment is not live but content is returned
        assert not self.assessment.live
        assert content["title"] == self.assessment.title
        assert content["high_result_page"] == {
            "id": self.high_result_page.id,
            "title": self.high_result_page.title,
        }
        assert content["high_inflection"] == 5.0
        assert content["medium_result_page"] == {
            "id": self.medium_result_page.id,
            "title": self.medium_result_page.title,
        }
        assert content["medium_inflection"] == 2.0
        assert content["low_result_page"] == {
            "id": self.low_result_page.id,
            "title": self.low_result_page.title,
        }

    # TODO: Add this test in once we've merged with main - there's some code in there that makes following the redirect work
    # def test_assessment_detail_endpoint_without_drafts(self, uclient, settings):
    #     """
    #     Unpublished assessments are not returned if the qa param is not set.
    #     """
    #     settings.STATIC_ROOT = Path("home/tests/test_static")
    #     self.assessment.unpublish()
    #     url = f"/api/v2/assessment/{self.assessment.id}"

    #     response = uclient.get(url, follow=True)

    #     assert response.status_code == 404

    def test_assessment_new_draft(self, uclient):
        """
        New revisions are returned if the qa param is set
        """
        high_result_page = ContentPage(
            title="new high result",
            slug="new-high-result",
            enable_whatsapp=True,
            whatsapp_body=[
                {
                    "type": "Whatsapp_Message",
                    "value": {
                        "message": "test message",
                        "buttons": [
                            {"type": "next_message", "value": {"title": "Tell me more"}}
                        ],
                    },
                }
            ],
        )
        homepage = HomePage.objects.first()
        homepage.add_child(instance=high_result_page)
        high_result_page.save_revision().publish()
        self.assessment.high_result_page = high_result_page
        self.assessment.high_inflection = 15.0
        self.assessment.medium_inflection = 12.0

        self.assessment.save_revision()

        response = uclient.get("/api/v2/assessment/")
        content = json.loads(response.content)

        assert self.assessment.live

        assert content["results"][0]["title"] == self.assessment.title
        assert content["results"][0]["high_result_page"] == {
            "id": self.high_result_page.id,
            "title": self.high_result_page.title,
        }
        assert content["results"][0]["high_inflection"] == 5.0
        assert content["results"][0]["medium_result_page"] == {
            "id": self.medium_result_page.id,
            "title": self.medium_result_page.title,
        }
        assert content["results"][0]["medium_inflection"] == 2.0
        assert content["results"][0]["low_result_page"] == {
            "id": self.low_result_page.id,
            "title": self.low_result_page.title,
        }

        response = uclient.get("/api/v2/assessment/?qa=True")
        content = json.loads(response.content)
        assert content["results"][0]["title"] == self.assessment.title
        assert content["results"][0]["high_result_page"] == {
            "id": high_result_page.id,
            "title": high_result_page.title,
        }
        assert content["results"][0]["high_inflection"] == 15.0
        assert content["results"][0]["medium_result_page"] == {
            "id": self.medium_result_page.id,
            "title": self.medium_result_page.title,
        }
        assert content["results"][0]["medium_inflection"] == 12.0
        assert content["results"][0]["low_result_page"] == {
            "id": self.low_result_page.id,
            "title": self.low_result_page.title,
        }
