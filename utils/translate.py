from google.cloud.translate_v3.services.translation_service import TranslationServiceAsyncClient


class GoogleTranslate:
    def __init__(self):
        self.translate_client = TranslationServiceAsyncClient()

