"""
Основная программа: читает письма из inbox, классифицирует, раскладывает по
папкам, ведёт лог и считает статистику.

Запуск:
    python3 sorter.py            # обычный запуск
    python3 sorter.py --dry-run  # показать, куда попадёт каждое письмо, но
                                 # ничего не перемещать

Используем только то, что было на занятиях: классы (ООП), работа с файлами и
папками (os, open), перемещение файлов, исключения, модуль sys для аргументов.
"""

import os
import sys

from email_message import read_email, EmailError
from classifier import Classifier


class MailSorter:
    """Связывает всё вместе: чтение -> классификация -> перемещение -> отчёт."""

    def __init__(self, inbox="inbox", dry_run=False):
        self.inbox = inbox            # папка с входящими письмами
        self.dry_run = dry_run        # режим "только показать, не перемещать"
        self.classifier = Classifier()
        self.log_lines = []           # строки для лог-файла
        # счётчик: категория -> сколько писем туда попало
        self.stats = {}
        self.broken = 0               # сколько файлов не удалось прочитать

    def log(self, message):
        """Записать строку в лог и вывести на экран."""
        print(message)
        self.log_lines.append(message)

    def make_folders(self):
        """Создать папки категорий (и папку broken для битых файлов)."""
        folders = self.classifier.categories()
        folders.append("broken")
        for name in folders:
            if not os.path.exists(name):
                os.makedirs(name)

    def move_file(self, filename, category):
        """Переместить файл из inbox в папку категории."""
        source = os.path.join(self.inbox, filename)
        target = os.path.join(category, filename)
        os.rename(source, target)

    def add_stat(self, category):
        """Увеличить счётчик категории на 1."""
        if category in self.stats:
            self.stats[category] = self.stats[category] + 1
        else:
            self.stats[category] = 1

    def run(self):
        """Обработать все письма из папки inbox."""
        if not os.path.exists(self.inbox):
            self.log("ОШИБКА: папка inbox не найдена: " + self.inbox)
            return

        if not self.dry_run:
            self.make_folders()

        files = sorted(os.listdir(self.inbox))
        self.log("Найдено файлов: " + str(len(files)))
        self.log("-" * 40)

        for filename in files:
            path = os.path.join(self.inbox, filename)
            if not os.path.isfile(path):
                continue                      # пропускаем папки, если попались

            # пробуем прочитать письмо
            try:
                email = read_email(path, filename)
            except EmailError as e:
                # битый/нечитаемый файл -> в папку broken, в лог пишем причину
                self.broken = self.broken + 1
                self.log(filename + " -> broken (" + str(e) + ")")
                if not self.dry_run:
                    self.move_file(filename, "broken")
                self.add_stat("broken")
                continue

            # классифицируем и перемещаем
            category = self.classifier.classify(email)
            self.log(filename + " -> " + category)
            if not self.dry_run:
                self.move_file(filename, category)
            self.add_stat(category)

        self.report()

    def report(self):
        """Вывести статистику и сохранить лог-файл."""
        self.log("-" * 40)
        self.log("ИТОГ:")
        total = 0
        for category in self.stats:
            total = total + self.stats[category]
        for category in sorted(self.stats):
            count = self.stats[category]
            self.log("  " + category + ": " + str(count))
        self.log("Всего обработано: " + str(total))
        self.log("Из них не удалось прочитать: " + str(self.broken))

        # сохраняем лог в файл (работа с файлами)
        if not self.dry_run:
            f = open("report.txt", "w", encoding="utf-8")
            f.write("\n".join(self.log_lines))
            f.close()
            self.log("Отчёт сохранён в report.txt")


def main():
    # простая обработка аргумента командной строки через sys.argv
    dry_run = False
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        dry_run = True

    sorter = MailSorter(inbox="inbox", dry_run=dry_run)
    sorter.run()


if __name__ == "__main__":
    main()
