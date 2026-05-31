import json

class EmailError(Exception):
    pass

class EmailMessage:
    def __init__(self, filename, subject="", sender="", body=""):
        self.filename = filename
        self.subject = subject
        self.sender = sender
        self.body = body

    def text(self):
        return (self.subject + " " + self.body).lower()
    
    def is_empty(self):
        """Пустое письмо — нет ни темы, ни текста."""
        return self.subject.strip() == "" and self.body.strip() == ""
    
    def __str__(self):
        return "Письмо '" + self.subject + "' от " + self.sender
    
SUBJECT_KEYS = ["subject", "тема"]
FROM_KEYS = ["from", "от кого", "от"]
SKIP_KEYS = ["to", "кому", "komu", "date", "дата", "ot kogo"]

def _parse_txt(filename, content):
    subject = ""
    sender = ""
    body_lines = []
    headers = True
    for line in content.split("\n"):
        if headers:
            if line.strip() == "":
                headers = False
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                if key in SUBJECT_KEYS:
                    subject = value
                    continue
                if key in FROM_KEYS:
                    sender = value
                    continue
                if key in SKIP_KEYS:
                    continue
                headers = False
                body_lines.append(line)
            else:
                headers = False
                body_lines.append(line)
        else:
            body_lines.append(line)
    body = "\n".join(body_lines).strip()
    return EmailMessage(filename, subject, sender, body)

def _parse_json(filename, content):
    data = json.loads(content)
    subject = str(data.get("subject", data.get("тема", "")))
    sender = str(data.get("from", data.get("от кого", "")))
    body = str(data.get("body", data.get("текст", "")))
    return EmailMessage(filename, subject, sender, body)

def read_email(path, filename):
    try:
        f = open(path, "r", encoding="utf-8")
        content = f.read()
        f.close()
    except Exception as e:
        raise EmailError("не удалось прочитать файл: " + str(e))
    if filename.lower().endswith(".json"):
        try:
            return _parse_json(filename, content)
        except Exception as e:
            raise EmailError("битый json: " + str(e))
    elif filename.lower().endswith(".txt"):
        return _parse_txt(filename, content)
    else:
        raise EmailError("неизвестный формат файла")