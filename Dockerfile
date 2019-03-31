FROM python:3.7-alpine

COPY ./requirements.txt /app/requirements.txt

RUN apk --no-cache add python3 && \
        apk --no-cache add --virtual install_deps git && \
        pip3 install -r /app/requirements.txt && \
        apk del install_deps

COPY . /app/

WORKDIR /app
CMD ["python3", "-u", "-m", "logger"]

