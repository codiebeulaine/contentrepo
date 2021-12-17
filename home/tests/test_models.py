from django.test import TestCase

from home.models import PageView
from .utils import create_page, create_page_rating


class ContentPageTests(TestCase):
    def test_page_and_revision_rating(self):
        page = create_page()

        self.assertEquals(page.page_rating, "(no ratings yet)")
        self.assertEquals(page.latest_revision_rating, "(no ratings yet)")

        create_page_rating(page)
        create_page_rating(page, False)
        create_page_rating(page)

        self.assertEquals(page.page_rating, "2/3 (66%)")
        self.assertEquals(page.latest_revision_rating, "2/3 (66%)")

        page.save_revision()
        create_page_rating(page)
        self.assertEquals(page.latest_revision_rating, "1/1 (100%)")

    def test_save_page_view(self):
        page = create_page()

        self.assertEquals(PageView.objects.count(), 0)

        page.save_page_view({"data__save": "this", "dont_save": "this"})

        self.assertEquals(PageView.objects.count(), 1)

        view = PageView.objects.last()
        self.assertEquals(view.page.id, page.id)
        self.assertEquals(view.revision.id, page.get_latest_revision().id)
        self.assertEquals(view.data, {"save": "this"})
