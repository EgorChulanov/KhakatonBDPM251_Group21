
import os
import sys
import logging

from email_message import read_email, EmailError
from classifier import Classifier


class MailSorter:
    def __init__(self, inbox="inbox", dry_run=False):
        self.inbox = inbox            # папка с входящими письмами
        self.dry_run = dry_run        # режим "только показать, не перемещать"
        self.classifier = Classifier()
        self.stats = {}
        self.broken = 0               # сколько файлов не удалось прочитать
        self.setup_logger()

    def setup_logger(self):          # настраиваем логгер
        self.logger = logging.getLogger("Message")
        self.logger.setLevel(logging.INFO)

        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        console = logging.StreamHandler()
        console.setFormatter(fmt)
        self.logger.addHandler(console)

        # хендлер «в файл» — только в боевом режиме (не в dry-run)
        if not self.dry_run:
            file_h = logging.FileHandler("report.txt", mode="w", encoding="utf-8")
            file_h.setFormatter(fmt)
            self.logger.addHandler(file_h)
        

    def make_folders(self):
        #Создать папки категорий (и папку broken для битых файлов)
        folders = self.classifier.categories()
        folders.append("broken")
        for name in folders:
            if not os.path.exists(name):
                os.makedirs(name)

    def move_file(self, filename, category):
        #Переместить файл из inbox в папку категории
        source = os.path.join(self.inbox, filename)
        target = os.path.join(category, filename)
        try:
            os.rename(source, target)
        except OSError as e:
            # сюда попадаем, ТОЛЬКО если внутри try возникла ошибка типа OSError
            # логируем объект ошибки
            self.logger.warning("возникла ошибка с перемещеннием файла: %s", e)


    def add_stat(self, category):
        #Увеличить счётчик категории на 1
        if category in self.stats:
            self.stats[category] = self.stats[category] + 1
        else:
            self.stats[category] = 1

    def run(self):
        #Обработать все письма из папки inbox
        if not os.path.exists(self.inbox):
            self.logger.error("ОШИБКА: папка inbox не найдена: " + self.inbox)
            return

        if not self.dry_run:
            self.make_folders()

        files = sorted(os.listdir(self.inbox))
        self.logger.info("Найдено файлов: " + str(len(files)))
        self.logger.info("-" * 40)

        for filename in files:
            path = os.path.join(self.inbox, filename)
            if not os.path.isfile(path):
                continue                      # пропускаем папки, если попались
            if filename.startswith("."):
                continue                      # не учитываем системные файлы

            # пробуем прочитать письмо
            try:
                email = read_email(path, filename)
            except EmailError as e:
                # битый/нечитаемый файл -> в папку broken, в лог пишем причину
                self.broken = self.broken + 1
                self.logger.warning(filename + " -> broken (" + str(e) + ")")
                if not self.dry_run:
                    self.move_file(filename, "broken")
                self.add_stat("broken")
                continue

            # классифицируем и перемещаем
            category = self.classifier.classify(email)
            self.logger.info(filename + " -> " + category)
            if not self.dry_run:
                self.move_file(filename, category)
            self.add_stat(category)

        self.report()

    def report(self):
        #Вывести статистику и сохранить лог-файл
        self.logger.info("-" * 40)
        self.logger.info("ИТОГ:")
        total = 0
        for category in self.stats:
            total = total + self.stats[category]
        for category in sorted(self.stats):
            count = self.stats[category]
            self.logger.info("  " + category + ": " + str(count))
        self.logger.info("Всего обработано: " + str(total))
        self.logger.info("Из них не удалось прочитать: " + str(self.broken))


def main():
    # простая обработка аргумента командной строки через sys.argv
    dry_run = False
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        dry_run = True

    sorter = MailSorter(inbox="inbox", dry_run=dry_run)
    sorter.run()


if __name__ == "__main__":
    main()
