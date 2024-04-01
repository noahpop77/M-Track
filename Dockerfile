FROM python:3.10

WORKDIR /app

RUN pip3 install flask requests mysql-connector-python

COPY . .

EXPOSE 80

WORKDIR /app/flask

CMD ["python3", "-u", "routes.py"]