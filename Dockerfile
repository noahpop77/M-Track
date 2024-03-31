FROM python:3.10

WORKDIR /app

RUN pip3 install flask

COPY . .

EXPOSE 80

CMD ["python3", "routes.py"]
