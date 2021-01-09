FROM python:3.8-alpine

# Installe les dépendances du projet
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY /src/ .

# Lance le serveur WSGI
CMD ["waitress-serve", "--listen=*:80", "app:WSGI"]
EXPOSE 80
