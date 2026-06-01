"""
Демонстрация ИИ-фич поверх базовой системы.

Берём несколько писем из inbox, классифицируем их базовым классификатором
(основной проект), а потом применяем ИИ-фичи в зависимости от категории:
  * important / requests -> черновик ответа + поиск задач со сроком;
  * important / spam     -> проверка на фишинг.

Запуск из папки проекта:
    python3 -m ai_features.demo
"""

import os
import sys

# чтобы видеть модули основного проекта (он на уровень выше этой папки)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_message import read_email, EmailError
from classifier import Classifier

from ai_features.gigachat_client import GigaChatClient
from ai_features.features import extract_tasks, check_phishing, draft_reply


def run(inbox="inbox", limit=5):
    classifier = Classifier()
    client = GigaChatClient()

    if not os.path.exists(inbox):
        print("Папка inbox не найдена:", inbox)
        return

    files = sorted(os.listdir(inbox))
    shown = 0

    for filename in files:
        if shown >= limit:
            break

        path = os.path.join(inbox, filename)
        if not os.path.isfile(path):
            continue

        try:
            email = read_email(path, filename)
        except EmailError:
            continue                      # битые письма для демо пропускаем

        category = classifier.classify(email)

        print("=" * 50)
        print("Письмо:", filename, "| категория:", category)
        print("Тема:", email.subject)

        if category in ("important", "requests"):
            print("\n[Черновик ответа]")
            print(draft_reply(email, client))
            print("\n[Задачи со сроком]")
            print(extract_tasks(email, client))

        if category in ("important", "spam"):
            print("\n[Проверка на фишинг]")
            print(check_phishing(email, client))

        print()
        shown += 1


if __name__ == "__main__":
    run()
