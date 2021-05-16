from rest_framework import serializers
from wagtail.api.v2.serializers import PageSerializer
from collections import OrderedDict


class TitleField(serializers.Field):
    """
    Serializes the "Title" field.
    """
    def get_attribute(self, instance):
        return instance

    def to_representation(self, page):
        request = self.context['request']
        if 'whatsapp' in request.GET and page.enable_whatsapp == True:
            if page.whatsapp_title:
                return page.whatsapp_title
        elif 'messenger' in request.GET and page.enable_messenger == True:
            if page.messenger_title:
                return page.messenger_title
        elif 'viber' in request.GET and page.enable_viber == True:
            if page.viber_title:
                return page.viber_title
        return page.title


class SubtitleField(serializers.Field):
    """
    Serializes the "Subtitle" field.
    """

    def get_attribute(self, instance):
        return instance

    def to_representation(self, page):
        request = self.context['request']
        if 'whatsapp' in request.GET and page.enable_whatsapp == True:
            if page.whatsapp_subtitle:
                return page.whatsapp_subtitle
        elif 'messenger' in request.GET and page.enable_messenger == True:
            if page.messenger_subtitle:
                return page.messenger_subtitle
        elif 'viber' in request.GET and page.enable_viber == True:
            if page.viber_subtitle:
                return page.viber_subtitle
        return page.subtitle


class BodyField(serializers.Field):
    """
    Serializes the "body" field.

    Example:
    "body": {
        "message": 1,
        "text": "body based on platform requested"
    }
    """
    def get_attribute(self, instance):
        return instance

    def to_representation(self, page):
        request = self.context['request']
        if 'message' in request.GET:
            message = int(request.GET['message'][0]) - 1
        else:
            message = 0
        if 'whatsapp' in request.GET and page.enable_whatsapp == True:
            if page.whatsapp_body != []:
                return OrderedDict([
                    ("message", message + 1),
                    ("text", page.whatsapp_body._raw_data[message]['value']),
                ])
        elif 'messenger' in request.GET and page.enable_messenger == True:
            if page.messenger_body != []:
                return OrderedDict([
                    ("message", message + 1),
                    ("text", page.messenger_body._raw_data[message]['value']),
                ])
        elif 'viber' in request.GET and page.enable_viber == True:
            if page.viber_body != []:
                return OrderedDict([
                    ("message", message + 1),
                    ("text", page.viber_body._raw_data[message]['value']),
                ])
        return OrderedDict([
            ("text", page.body._raw_data),
        ])


class ContentPageSerializer(PageSerializer):
    title = TitleField(read_only=True)
    subtitle = SubtitleField(read_only=True)
    body = BodyField(read_only=True)
