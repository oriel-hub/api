FROM python:3.6-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /var/django
WORKDIR /var/django

# Installing OS Dependencies
## https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=891488
RUN bash -c 'mkdir -p /usr/share/man/man{1,7}'
RUN apt-get update && apt-get upgrade -qq -y && apt-get install -y \
  git libmariadb-dev-compat gcc make sudo mariadb-client rsync curl \
  locales wkhtmltopdf

RUN localedef -i en_GB -f UTF-8 en_GB.UTF-8
ENV LC_ALL=en_GB.UTF-8
ENV LANG=en_GB.UTF-8
ENV LANGUAGE=en_GB.UTF-8

# Uncomment this when https://github.com/pypa/pipenv/issues/2924 is resolved:
# RUN pip install --upgrade pip
# RUN pip install pipenv isort
# COPY Pipfile /var/django
# RUN pipenv install --verbose --sequential --dev --python 3.6

RUN echo "[client]\npassword=password" > /root/.my.cnf
RUN echo "password" > /root/mysql_root_password

# Django service
EXPOSE 8000
STOPSIGNAL SIGINT
#ENTRYPOINT ["pipenv", "run", "./manage.py"]
#CMD ["runserver", "0.0.0.0:8000"]
