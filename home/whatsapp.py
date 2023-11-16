import json
import mimetypes
from collections.abc import Iterable
from enum import Enum
from typing import Any
from urllib.parse import urljoin

import requests
from django.conf import settings  # type: ignore
from wagtail.images import get_image_model  # type: ignore
from wagtail.models import Locale  # type: ignore

from .constants import WHATSAPP_LANGUAGE_MAPPING


class WhatsAppLanguage(Enum):
    """
    These are the languages supported by WhatsApp message templates as per
    https://developers.facebook.com/docs/whatsapp/api/messages/message-templates#supported-languages
    (Fetched 2023-11-16)
    """

    af = "af"  # Afrikaans
    sq = "sq"  # Albanian
    ar = "ar"  # Arabic
    az = "az"  # Azerbaijani
    bn = "bn"  # Bengali
    bg = "bg"  # Bulgarian
    ca = "ca"  # Catalan
    zh_CN = "zh_CN"  # Chinese (CHN)
    zh_HK = "zh_HK"  # Chinese (HKG)
    zh_TW = "zh_TW"  # Chinese (TAI)
    hr = "hr"  # Croatian
    cs = "cs"  # Czech
    da = "da"  # Danish
    nl = "nl"  # Dutch
    en = "en"  # English
    en_GB = "en_GB"  # English (UK)
    en_US = "en_US"  # English (US)
    et = "et"  # Estonian
    fil = "fil"  # Filipino
    fi = "fi"  # Finnish
    fr = "fr"  # French
    ka = "ka"  # Georgian
    de = "de"  # German
    el = "el"  # Greek
    gu = "gu"  # Gujarati
    ha = "ha"  # Hausa
    he = "he"  # Hebrew
    hi = "hi"  # Hindi
    hu = "hu"  # Hungarian
    id = "id"  # Indonesian
    ga = "ga"  # Irish
    it = "it"  # Italian
    ja = "ja"  # Japanese
    kn = "kn"  # Kannada
    kk = "kk"  # Kazakh
    rw_RW = "rw_RW"  # Kinyarwanda
    ko = "ko"  # Korean
    ky_KG = "ky_KG"  # Kyrgyz (Kyrgyzstan)
    lo = "lo"  # Lao
    lv = "lv"  # Latvian
    lt = "lt"  # Lithuanian
    mk = "mk"  # Macedonian
    ms = "ms"  # Malay
    ml = "ml"  # Malayalam
    mr = "mr"  # Marathi
    nb = "nb"  # Norwegian
    fa = "fa"  # Persian
    pl = "pl"  # Polish
    pt_BR = "pt_BR"  # Portuguese (BR)
    pt_PT = "pt_PT"  # Portuguese (POR)
    pa = "pa"  # Punjabi
    ro = "ro"  # Romanian
    ru = "ru"  # Russian
    sr = "sr"  # Serbian
    sk = "sk"  # Slovak
    sl = "sl"  # Slovenian
    es = "es"  # Spanish
    es_AR = "es_AR"  # Spanish (ARG)
    es_ES = "es_ES"  # Spanish (SPA)
    es_MX = "es_MX"  # Spanish (MEX)
    sw = "sw"  # Swahili
    sv = "sv"  # Swedish
    ta = "ta"  # Tamil
    te = "te"  # Telugu
    th = "th"  # Thai
    tr = "tr"  # Turkish
    uk = "uk"  # Ukrainian
    ur = "ur"  # Urdu
    uz = "uz"  # Uzbek
    vi = "vi"  # Vietnamese
    zu = "zu"  # Zulu

    @classmethod
    def from_locale(cls, locale: Locale) -> "WhatsAppLanguage":
        lc = WHATSAPP_LANGUAGE_MAPPING.get(locale.language_code, locale.language_code)
        # This will raise KeyError for unsupported languages.
        return cls[lc]


def create_whatsapp_template(
    name: str,
    body: str,
    category: str,
    locale: Locale | None = None,
    quick_replies: Iterable[str] = (),
    image_id: int | None = None,
    example_values: Iterable[str] | None = None,
) -> None:
    """
    Create a WhatsApp template through the WhatsApp Business API.

    FIXME: Do we want locale to be optional?
    """
    if locale is None:
        locale = Locale.objects.get(language_code="en")

    url = urljoin(
        settings.WHATSAPP_API_URL,
        f"graph/v14.0/{settings.FB_BUSINESS_ID}/message_templates",
    )
    headers = {
        "Authorization": "Bearer {}".format(settings.WHATSAPP_ACCESS_TOKEN),
        "Content-Type": "application/json",
    }

    components: list[dict[str, Any]] = []
    if example_values:
        components.append(
            {
                "type": "BODY",
                "text": body,
                "example": {
                    "body_text": [example_values],
                },
            }
        )
    else:
        components.append({"type": "BODY", "text": body})

    if quick_replies:
        buttons = []
        for button in quick_replies:
            buttons.append({"type": "QUICK_REPLY", "text": button})
        components.append({"type": "BUTTONS", "buttons": buttons})

    if image_id:
        image_handle = upload_image(image_id)
        components.append(
            {
                "type": "HEADER",
                "format": "IMAGE",
                "example": {"header_handle": [image_handle]},
            }
        )

    data = {
        "category": category,
        "name": name.lower(),
        "language": WhatsAppLanguage.from_locale(locale).value,
        "components": components,
    }
    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(data, indent=4),
    )
    response.raise_for_status()


def get_upload_session_id(image_id: int) -> dict[str, Any]:
    url = urljoin(
        settings.WHATSAPP_API_URL,
        "graph/v14.0/app/uploads",
    )
    headers = {
        "Content-Type": "application/json",
    }

    img_obj = get_image_model().objects.get(id=image_id)
    mime_type = mimetypes.guess_type(img_obj.file.name)[0]
    file_size = img_obj.file.size

    data = {
        "file_length": file_size,
        "file_type": mime_type,
        "access_token": settings.WHATSAPP_ACCESS_TOKEN,
        "number": settings.FB_BUSINESS_ID,
    }

    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(data, indent=4),
    )

    upload_details = {
        "upload_session_id": response.json()["id"],
        "upload_file": img_obj.file,
    }

    response.raise_for_status()
    return upload_details


def upload_image(image_id: int) -> str:
    upload_details = get_upload_session_id(image_id)
    url = urljoin(
        settings.WHATSAPP_API_URL,
        f"graph/{upload_details['upload_session_id']}",
    )

    headers = {
        "file_offset": "0",
    }
    files_data = {
        "file": (upload_details["upload_file"]).open("rb"),
    }
    form_data = {
        "number": settings.FB_BUSINESS_ID,
        "access_token": settings.WHATSAPP_ACCESS_TOKEN,
    }
    response = requests.post(url=url, headers=headers, files=files_data, data=form_data)
    response.raise_for_status()
    return response.json()["h"]
