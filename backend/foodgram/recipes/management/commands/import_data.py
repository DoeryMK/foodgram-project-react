import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag
from users.models import User


FILES = {
    Ingredient: (
        'ingredients.csv', (
            'name', 'measurement_unit', 'None', 'None', 'None'
        )
    ),
    Tag: (
        'tags.csv', (
            'name', 'color', 'slug', 'None', 'None'
        )
    ),
    User: (
        'users.csv', (
            'username', 'email', 'first_name', 'last_name', 'password'
        )
    ),
}


class Command(BaseCommand):
    help = 'Импорт данных из csv-файлов'
    path_parent = Path(settings.BASE_DIR).parent

    def handle(self, *args, **options):
        for entity, file in FILES.items():
            file_path = f"{settings.BASE_DIR}/recipes/data/{file[0]}"
            with open(file_path, encoding="utf8") as f:
                for row in csv.reader(f, delimiter=','):
                    name = row[0]
                    attrs = dict(zip(file[1], row))
                    print(f'Добавление объекта "{name}" в БД')
                    entity.objects.create(**attrs)
                    if entity == User:
                        username = attrs.get('username')
                        password = attrs.get('password')
                        u = User.objects.get(username=username)
                        u.set_password(password)
                        u.save()

        for entity in FILES:
            result = entity.objects.count()
            print(f'Добавлено {result} новых объекта класса {entity} в БД')
