FROM python:3
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . ./
COPY ./.env ./.env
EXPOSE 8000