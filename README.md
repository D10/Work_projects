## Создаем пользователя, настраиваем SSH

```
sudo apt-get update ; \
sudo apt-get install -y vim mosh tmux htop git curl wget unzip zip gcc build-essential make
```

##Настройка SSH

```
sudo vim /etc/ssh/sshd_config
    AllowUsers www
    PermitRootLogin no
    PasswordAuthentication no
```

##Перезапускаем SSH сервер, задаем пароль для пользователя www

```
sudo service ssh restart
sudo passwd www
```

## Делаем установку необходимых для работы сервера программ

```
sudo apt-get install -y zsh tree redis-server nginx zlib1g-dev libbz2-dev libreadline-dev llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev liblzma-dev python3-dev python-imaging python3-lxml libxslt-dev python-libxml2 python-libxslt1 libffi-dev libssl-dev python-dev gnumeric libsqlite3-dev libpq-dev libxml2-dev libxslt1-dev libjpeg-dev libfreetype6-dev libcurl4-openssl-dev supervisor
```

## Установим zsh

```
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
```

## Поставим команду clear для очистки терминала

```
vim ~/.zshrc
    alias cls="clear"
```

## Устанавливаем Python3.7

mkdir ~/code

```
wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tgz ; \
tar xvf Python-3.7.* ; \
cd Python-3.7.3 ; \
mkdir ~/.python ; \
./configure --enable-optimizations --prefix=/home/www/.python ; \
make -j8 ; \
sudo make altinstall
```

Теперь python3.7 находится в следующем пути `/home/www/.python/bin/python3.7`. Обновим pip:

```
sudo /home/www/.python/bin/python3.7 -m pip install -U pip
```

Теперь создадим папку для нашего проекта и установим из GitHub наш проект и создадим виртуальное окружение

```
cd code
git clone project_git
cd project_dir
python3.7 -m venv env
. ./env/bin/activate
```

## Устанавливаем и настраиваем Базу Данных PostgreSQL


```
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add - ; \
RELEASE=$(lsb_release -cs) ; \
echo "deb http://apt.postgresql.org/pub/repos/apt/ ${RELEASE}"-pgdg main | sudo tee  /etc/apt/sources.list.d/pgdg.list ; \
sudo apt update ; \
sudo apt -y install postgresql-11 ; \
sudo localedef ru_RU.UTF-8 -i ru_RU -fUTF-8 ; \
export LANGUAGE=ru_RU.UTF-8 ; \
export LANG=ru_RU.UTF-8 ; \
export LC_ALL=ru_RU.UTF-8 ; \
sudo locale-gen ru_RU.UTF-8 ; \
sudo dpkg-reconfigure locales
```

```
sudo vim /etc/profile
    export LANGUAGE=ru_RU.UTF-8
    export LANG=ru_RU.UTF-8
    export LC_ALL=ru_RU.UTF-8
```

Сменим пароль для пользователя `postges`, создадим чистую базу данных `dbms_db`:

```
sudo passwd postgres
su - postgres
export PATH=$PATH:/usr/lib/postgresql/11/bin
createdb --encoding UNICODE dbms_db --username postgres
exit
```

Создадим пользователя БД `dbms` и дадим ему полные привилегии:

```
sudo -u postgres psql
postgres=# ...
create user dbms with password 'some_password';
ALTER USER dbms CREATEDB;
grant all privileges on database dbms_db to dbms;
\c dbms_db
GRANT ALL ON ALL TABLES IN SCHEMA public to dbms;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public to dbms;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to dbms;
CREATE EXTENSION pg_trgm;
ALTER EXTENSION pg_trgm SET SCHEMA public;
UPDATE pg_opclass SET opcdefault = true WHERE opcname='gin_trgm_ops';
\q
exit
```

Для тестового соединения с нашей БД в файле `~/.pgpass` запишем наши данные авторизации для быстрого соединения

```
vim ~/.pgpass
	localhost:5432:dbms_db:dbms:some_password
chmod 600 ~/.pgpass
psql -h localhost -U dbms dbms_db
```

## Устанавливаем и конфигурируем supervisor

```
sudo apt install supervisor

vim /home/www/code/project/bin/start_gunicorn.sh
	#!/bin/bash
	source /home/www/code/project/env/bin/activate
	source /home/www/code/project/env/bin/postactivate
	exec gunicorn  -c "/home/www/code/project/gunicorn_config.py" project.wsgi

chmod +x /home/www/code/project/bin/start_gunicorn.sh

vim project/supervisor.salesbeat.conf
	[program:www_gunicorn]
	command=/home/www/code/project/bin/start_gunicorn.sh
	user=www
	process_name=%(program_name)s
	numprocs=1
	autostart=true
	autorestart=true
	redirect_stderr=true
```

Настройка для gunicorn_config.py

```
command = '/home/www/code/project/env/bin/gunicorn'
pythonpath = '/home/www/code/project/project'
bind = '127.0.0.1:8001'
workers = 3
user = 'www'
limit_request_fields = 32000
limit_request_field_size = 0
raw_env = 'DJANGO_SETTINGS_MODULE=project.settings'
```

## О проекте:

В нашем проекте реализованы 3 модели: news, users, Tokens
В качестве примера миграций моделей продемонстрирую небольшие изминения в модели news
![Изначальная модель](https://user-images.githubusercontent.com/79451112/118439806-f7240b80-b6e6-11eb-8f65-c440ba39decc.png)

Добавим в модель новое поле, которое будет отображать дату редактирования новости(updated_at) и изменим максимальную длину строки для заголовка новости(title)

![Измененная модель](https://user-images.githubusercontent.com/79451112/118439939-32263f00-b6e7-11eb-8025-9559522a6d43.png)

В терминале пропишем следующие команды:

```
python manage.py makemigrations
python manage.py migrate
```

Таким образом мы собираем все изменения в моделях и мигрируем их
Обновленный файл с миграциями мы увидим в директории нашего приложения в папке migrations:

![Migrations](https://user-images.githubusercontent.com/79451112/118440170-8d583180-b6e7-11eb-8bb7-a37193369482.png)


## Проверка API запросов сайта

Проверим соединение, открываем браузер и вводим в адресную строку адрес: 84.252.142.103

Далее откроем сайт web.postman.co и в нем откроем Workspace

внутри Workspace создаем вкладку и вставляем туда следующий адрес:

```
http://84.252.142.103/api/v1/news/
```

Устанавливаем тип запроса GET и нажимаем Send

![Результат GET запроса без авторизации](https://user-images.githubusercontent.com/79451112/118439555-81b83b00-b6e6-11eb-9438-81e9a6716312.png)

Как мы видим, список новостей нам недоступен

Откроем новвую вкладку с адресом авторизации:

```
http://84.252.142.103/auth/token/login
```

В ней откроем вкладку Body, выберем пункт form-data и внутри полей формы напишем поля авторизации (username, password) и соответствующие им данные

Выбираем тип запроса POST и нажимаем Send

В появившемся окне видим токен авторизации

![Токен авторизации](https://user-images.githubusercontent.com/79451112/118440500-0d7e9700-b6e8-11eb-910b-20f9069c5be4.png)

Если мы в браузере откроем панель администрации нашего сайта (http://84.252.142.103/admin) и авторизуемся, то в БЛ Tokens мы увидим токен авторизованного нами пользователя. Токен НЕ сохраняется после запроса logout

![Токен в админке](https://user-images.githubusercontent.com/79451112/118440732-65b59900-b6e8-11eb-8bfc-e6bfca59b301.png)

Теперь если мы снова откроем в postman вкладку http://84.252.142.103/api/v1/news/ во вкладке headers в поле Authorization укажем наш токен и снова отправим GET запрос, то получим наш список новостей, т.к теперь сайт видит, что мы авторизованы и открвает нам доступ к странице

![Список новостей](https://user-images.githubusercontent.com/79451112/118440936-baf1aa80-b6e8-11eb-82be-db6b6e39f705.png)





