import pytest

from email_message import EmailMessage, read_email, EmailError


def test_text():
    email = EmailMessage("f", "Hello", "u@u.ru", "WORLD")
    assert email.text() == "hello world"


@pytest.mark.parametrize("subject, body, expected", [
    ("", "", True),
    ("x", "", False),
    ("  ", "  ", True),
])
def test_is_empty(subject, body, expected):
    email = EmailMessage("f", subject, "u@u.ru", body)
    assert email.is_empty() == expected


def test_read_txt(tmp_path):
    p = tmp_path / "letter.txt"
    p.write_text("Subject: тест\nFrom: a@b.ru\n\nтело письма", encoding="utf-8")
    email = read_email(str(p), "letter.txt")
    assert email.subject == "тест"
    assert email.sender == "a@b.ru"
    assert "тело письма" in email.body


def test_read_txt_russian(tmp_path):
    p = tmp_path / "letter.txt"
    p.write_text("Тема: заявка\nОт кого: ivan@b.ru\n\nпрошу доступ", encoding="utf-8")
    email = read_email(str(p), "letter.txt")
    assert email.subject == "заявка"
    assert email.sender == "ivan@b.ru"


def test_read_json(tmp_path):
    p = tmp_path / "mail.json"
    p.write_text('{"subject": "Счёт", "from": "x@y.ru", "body": "оплата"}', encoding="utf-8")
    email = read_email(str(p), "mail.json")
    assert email.subject == "Счёт"
    assert email.sender == "x@y.ru"
    assert "оплата" in email.body


def test_unknown_format_raises(tmp_path):
    p = tmp_path / "mail.xyz"
    p.write_text("что-то", encoding="utf-8")
    with pytest.raises(EmailError):
        read_email(str(p), "mail.xyz")


def test_broken_json_raises(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{не json", encoding="utf-8")
    with pytest.raises(EmailError):
        read_email(str(p), "bad.json")
