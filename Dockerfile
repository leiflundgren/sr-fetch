# syntax=docker/dockerfile:1
# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim


WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

CMD [ "python3", "-m" , "flask", "run"]

#EXPOSE 5002
#
## Keeps Python from generating .pyc files in the container
#ENV PYTHONDONTWRITEBYTECODE=1
#
## Turns off buffering for easier container logging
#ENV PYTHONUNBUFFERED=1
#
## Install pip requirements
#COPY requirements.txt .
#RUN python -m pip install -r requirements.txt
#
#WORKDIR /app
#COPY . /app
#
## Creates a non-root user with an explicit UID and adds permission to access the /app folder
## For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
#USER appuser
#
## During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
##CMD ["gunicorn", "--bind", "localhost:5002", "app_factory:app"]
#CMD [ "python3", "-m" , "flask", "run", "--host=localhost:5002"]