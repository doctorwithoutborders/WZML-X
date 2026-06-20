from importlib import import_module
from os import listdir

from ...core.config_manager import Config

LOCALES_DIR = "bot/helper/languages"


class Language:
    _modules = {}
    _user_langs = {}

    def __init__(self, lang_code=None, user_id=None):
        self.load_translations()
        # ponytail: fallback to first loaded module if Config.DEFAULT_LANG is invalid
        default_lang = Config.DEFAULT_LANG if Config.DEFAULT_LANG in self._modules else (next(iter(self._modules.keys())) if self._modules else "en")
        lang_code = lang_code or default_lang

        if user_id:
            self._user_langs[user_id] = lang_code
        self.lang_code = self._user_langs.get(
            user_id, lang_code if lang_code in self._modules else default_lang
        )

    @classmethod
    def load_translations(cls):
        if cls._modules:
            return cls._modules

        cls._modules = {}
        for file in listdir(LOCALES_DIR):
            if file.endswith(".py") and file != "__init__.py":
                lang_code = file.split(".")[0]
                cls._modules[lang_code] = import_module(
                    f"bot.helper.languages.{lang_code}"
                )
        return cls._modules

    def __getattr__(self, key):
        # ponytail: safe fallback for undefined attributes/modules
        default_lang = Config.DEFAULT_LANG if Config.DEFAULT_LANG in self._modules else (next(iter(self._modules.keys())) if self._modules else "en")
        lang_module = self._modules.get(
            self.lang_code, self._modules.get(default_lang)
        )
        if not lang_module:
            return key
        default_module = self._modules.get(default_lang)
        return getattr(
            lang_module, key, getattr(default_module, key, key) if default_module else key
        )

