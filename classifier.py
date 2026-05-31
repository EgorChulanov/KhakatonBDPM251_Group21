"""
Классификатор писем по правилам.

Идея простая: для каждой категории заданы ключевые слова. Смотрим, слова какой
категории встречаются в письме, и относим письмо туда, где совпадений больше.
Если совпадений нет совсем — письмо идёт в категорию "other" (на ручной разбор),
чтобы ни одно письмо не потерялось. Это и есть устойчивость классификации:
система не угадывает наугад, а честно откладывает непонятное письмо.

Используем только класс и словарь со списками — всё это было на занятиях (ООП).
"""


class Classifier:
    """Раскладывает письма по категориям на основе ключевых слов."""

    def __init__(self):
        # категория -> список ключевых слов (маленькими буквами)
        self.rules = {
            "important": [
                "urgent", "critical", "срочно", "критич", "инцидент",
                "не работает", "не отвечает", "недоступ", "падает", "сбой",
                "остановлена", "disk usage", "массовый сбой",
            ],
            "requests": [
                "не могу", "нет доступа", "запрос доступа", "выдать права",
                "права в", "проблема", "ошибка", "не запускается",
                "неисправность", "помогите", "вопрос", "установк", "не войти",
                "войти в",
            ],
            "spam": [
                "выиграли", "iphone", "розыгрыш", "offer", "exclusive",
                "поздравляем", "приз", "бесплатно", "скидк", "верификация аккаунта",
                "limited time",
            ],
            "notifications": [
                "дайджест", "[info]", "мониторинг", "плановый отчёт",
                "no-reply", "noreply", "monitoring.internal", "grafana",
                "alerts@", "уведомление",
            ],
        }

    def classify(self, email):
        """Вернуть название категории для письма (строку)."""
        # пустое письмо отдельно — анализировать нечего
        if email.is_empty():
            return "other"

        text = email.text()

        best_category = "other"
        best_count = 0

        # считаем совпадения по каждой категории
        for category in self.rules:
            count = 0
            for word in self.rules[category]:
                if word in text:
                    count = count + 1
            if count > best_count:
                best_count = count
                best_category = category

        # ещё одна проверка: письма от автоматических адресов — это уведомления
        if best_count == 0:
            sender = email.sender.lower()
            if "no-reply" in sender or "noreply" in sender or "alerts@" in sender or "monitoring" in sender:
                return "notifications"

        return best_category

    def categories(self):
        """Список всех папок, которые может создать классификатор."""
        result = list(self.rules.keys())
        result.append("other")     # для писем без совпадений
        return result
