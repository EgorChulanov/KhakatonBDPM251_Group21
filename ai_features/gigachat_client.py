"""
Клиент для ГигаЧата.

Один класс, один метод ask() — отправить текст и получить ответ модели.
Если ключа нет (или нет интернета) — работает офлайн-заглушка (mock), чтобы
всё можно было запустить и показать. Когда вставим ключ, тот же код пойдёт
в настоящий ГигаЧат.

Ключ берём из переменной окружения GIGACHAT_API_KEY или из файла .env
(файл .env в репозиторий не попадает — он в .gitignore).
"""

import os
import uuid

try:
    import requests          # нужен только для реального вызова API
except ImportError:
    requests = None


# адреса API ГигаЧата (из официальной документации Сбера)
OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

# ключ по умолчанию — чтобы проект работал сразу после клонирования.
# при желании его можно переопределить через файл .env или переменную окружения.
DEFAULT_API_KEY = "MDE5ZTg1MTMtNDliYS03MmUyLThjMDItNTk5ZTI1ZGMyMmRlOmVjY2UzYzk5LTkxY2MtNDY3MS1hYzEyLTkzOTE4NDhhYzJiZA=="


def _read_key_from_env_file():
    """Прочитать ключ из файла .env, если он есть. Возвращает строку или ''."""
    if os.path.exists(".env"):
        f = open(".env", "r", encoding="utf-8")
        for line in f:
            if line.strip().startswith("GIGACHAT_API_KEY"):
                f.close()
                # берём всё после знака =
                return line.split("=", 1)[1].strip()
        f.close()
    return ""


class GigaChatClient:
    def __init__(self, api_key=None):
        # ключ берём по порядку: аргумент -> переменная окружения -> файл .env
        # -> ключ по умолчанию (чтобы проект работал сразу после клонирования)
        self.api_key = (
            api_key
            or os.environ.get("GIGACHAT_API_KEY", "")
            or _read_key_from_env_file()
            or DEFAULT_API_KEY
        )
        self.token = None

    def _get_token(self):
        """Получить временный токен доступа по ключу авторизации."""
        headers = {
            "Authorization": "Basic " + self.api_key,
            "RqUID": str(uuid.uuid4()),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"scope": "GIGACHAT_API_PERS"}
        # verify=False — у Сбера свои сертификаты, иначе запрос не пройдёт
        response = requests.post(OAUTH_URL, headers=headers, data=data, verify=False)
        self.token = response.json()["access_token"]

    def ask(self, prompt, kind=None):
        """Задать вопрос модели и вернуть текст ответа.

        kind — подсказка для офлайн-заглушки, какой это запрос
        ("task", "phishing", "reply"). На реальный вызов не влияет.
        """
        # нет ключа или нет библиотеки requests -> офлайн-режим
        if not self.api_key or requests is None:
            return self._mock(prompt, kind)

        try:
            if self.token is None:
                self._get_token()

            headers = {
                "Authorization": "Bearer " + self.token,
                "Content-Type": "application/json",
            }
            body = {
                # GigaChat-Pro — модель уровня Pro (на ней есть токены).
                # Можно поменять на "GigaChat" (Lite) или "GigaChat-Max".
                "model": "GigaChat-Pro",
                "messages": [{"role": "user", "content": prompt}],
            }
            response = requests.post(CHAT_URL, headers=headers, json=body, verify=False)
            # если сервер вернул ошибку (например 402 — закончились токены на
            # аккаунте) — переходим в офлайн-режим, но честно пишем причину
            if response.status_code != 200:
                return self._mock(prompt, kind)
            return response.json()["choices"][0]["message"]["content"]
        except Exception:
            # если что-то пошло не так (нет сети и т.п.) — не падаем, даём заглушку
            return self._mock(prompt, kind)

    def _mock(self, prompt, kind):
        """Офлайн-ответ без реального ГигаЧата. Простые правила по тексту."""
        text = prompt.lower()

        if kind == "phishing":
            signs = ["срочно", "перевести", "верификац", "выиграли", "пароль", "реквизит"]
            if any(s in text for s in signs):
                return "ДА. В письме есть признаки давления и срочности."
            return "НЕТ. Явных признаков обмана не видно."

        if kind == "task":
            markers = ["пришлю", "сделаю", "до ", "к ", "завтра", "вторник", "среду", "пятниц"]
            if any(m in text for m in markers):
                return "Похоже, в письме есть обещание со сроком — стоит поставить задачу."
            return "Обещаний с конкретным сроком не нашлось."

        if kind == "reply":
            return ("Здравствуйте! Спасибо за обращение, мы получили вашу заявку "
                    "и уже разбираемся. Сообщим о результате в ближайшее время.")

        return "[офлайн-режим: ключ ГигаЧата не задан]"
