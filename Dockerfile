FROM python:3.10

WORKDIR /app

RUN pip3 install flask requests mysql-connector

COPY . .

RUN pwd
RUN ls -la
RUN cat config.ini

EXPOSE 80

WORKDIR /app/flask

CMD ["python3", "routes.py"]
