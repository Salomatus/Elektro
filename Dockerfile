FROM python:3.11
FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf

COPY html/ /usr/share/nginx/html/

EXPOSE 80

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .