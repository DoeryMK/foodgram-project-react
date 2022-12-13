import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from django.conf import settings

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт Ингредиентов из csv-файла'
    path_parent = Path(settings.BASE_DIR).parent
    file_path = (path_parent / "../data/ingredients.csv").resolve()

    def handle(self, *args, **options):
        with open(self.file_path, encoding="utf8") as f:

            for row in csv.reader(f, delimiter=','):
                name, measurement_unit = row
                print(f'Добавление {name} - {measurement_unit} в БД')
                Ingredient.objects.create(
                    name=name,
                    measurement_unit=measurement_unit)

            result = Ingredient.objects.count()
            print(f'Добавлено {result} новых записей в БД')
