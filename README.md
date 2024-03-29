# Дипломный проект курса Python-разработчик ЯП

## **Основная цель проекта**

Проект выполнен с целью закрепления и демонстрации полученных в ходе обучения 
знаний по разработке бекенда для сайта на Django. API реализован с 
помощью DRF в соответствии с предоставленным ТЗ. 
Выполнен деплой на боевой сервер с использованием Docker-контейнеров.
Фронтенд был предварительно подготовлен ЯП.

###  **Краткое описание**
- Ресурс позволяет зарегистрированным пользователям публиковать, редактировать и удалять рецепты.
- Пользователи могут подписываться/отписываться на/от интересных авторов, добавлять/удалять понравившиеся рецепты в избранное, а также в корзину. 
- Пользователю доступно сохранение списка ингредиентов в формате txt на устройство, через которое был выполнен вход на сайт. 
Список формируется на основе ингредиентов из добавленных в корзину рецептов.
- Неавторизованные пользователи могут просматривать опубликованные рецепты.
- Доступна регистрация и аутентификация пользователей.

Проект доступен по [адресу](http://ypyield.ddns.net/)

### _Основные файлы для развертывания проекта_  
- Dockerfile - инструкции, которые используются для создания образа бекенда и фронтенда 
- Docker-compose.yml - инструкции, которые используются для развертывания проекта на боевом сервере в нескольких контейнерах: db, backend, nginx, frontend  

## **Технологии**
Django  
Django Rest Framework  
Docker  
Nginx  
Gunicorn  
Postgres  

## **Запуск проекта**
Выполните следующие команды в терминале:

1. Клонировать проект из репозитория
```
git@github.com:DoeryMK/foodgram-project-react.git
```
или
```
https://github.com/DoeryMK/foodgram-project-react.git
```
2. Перейти в папку infra и создать файл «.env», добавив в него переменные окружения. 
```
cd infra
```
```
touch .env
```
3. Выполнить команду запуска docker-compose в «фоновом режиме»
```
docker-compose up -d --build
```
После сборки контейнеров необходимо подготовить БД, выполнив следующее:

1. Внутри контейнера backend выполнить миграции
```
docker-compose exec backend python manage.py migrate
```
2. Внутри контейнера backend создать суперпользователя
```
docker-compose exec backend python manage.py createsuperuser
```
3. Внутри контейнера backend выполнить команду сбора статики
```
docker-compose exec backend python manage.py collectstatic --no-input 
```
4. Внутри контейнера backend выполнить команду для заполнения БД тестовыми данными
```
docker-compose exec backend python manage.py import_data
```
5. Чтобы сделать резервную копию базы данных, выполните команду
```
docker-compose exec backend python manage.py dumpdata > fixtures.json
```

### _Описание шаблона .env_
Необходимо указать переменные окружения в следующем формате:

DB_ENGINE=*СУБД*  
DB_NAME=*имя БД*  
POSTGRES_USER=*логин для подключения к БД*  
POSTGRES_PASSWORD=*пароль для подключения к БД*  
DB_HOST=*название сервиса (контейнера)*  
DB_PORT=*порт для подключения к БД*  
SECRET_KEY = *уникальный секретный ключ Django*  

### _Наполнение БД данными_ 
Операция выполняется с помощью management-команды. 
Данный загружаются из заранее подготовленных файлов: tags.csv, ingredients.csv, users.csv

## Авторы: [DoeryMK](https://github.com/DoeryMK) 