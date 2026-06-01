import pytest

from email_message import EmailMessage
from classifier import Classifier


@pytest.fixture
def classifier():
    return Classifier()


@pytest.mark.parametrize("subject, body, expected", [
    ("Срочно! сервер не работает", "критический инцидент", "important"),
    ("Не могу войти", "нет доступа", "requests"),
    ("Вы выиграли iPhone", "розыгрыш бесплатно", "spam"),
    ("Дайджест", "[info] мониторинг", "notifications"),
])
def test_classify_categories(classifier, subject, body, expected):
    email = EmailMessage("f", subject, "u@u.ru", body)
    assert classifier.classify(email) == expected


def test_no_match_other(classifier):
    email = EmailMessage("f", "Привет", "u@u.ru", "как дела")
    assert classifier.classify(email) == "other"


def test_empty_other(classifier):
    email = EmailMessage("f", "", "u@u.ru", "")
    assert classifier.classify(email) == "other"


def test_noreply_sender(classifier):
    # без ключевых слов, но адрес автоматический -> notifications
    email = EmailMessage("f", "Привет", "no-reply@monitoring.internal", "тест")
    assert classifier.classify(email) == "notifications"


def test_categories_has_other(classifier):
    assert "other" in classifier.categories()
