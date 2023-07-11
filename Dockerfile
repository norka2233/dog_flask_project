FROM python:slim

RUN useradd dog_flask_project

WORKDIR /home/dog_flask_project

COPY requirements.txt requirements.txt
RUN python3 -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql cryptography

COPY app app
COPY migrations migrations
COPY dogFlaskProject.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP dogFlaskProject.py

RUN chown -R dog_flask_project:dog_flask_project ./
USER dog_flask_project

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]