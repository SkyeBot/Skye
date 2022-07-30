FROM python:3.10-alpine
RUN apk add --no-cache linux-headers && apk --no-cache add gcc musl-dev && apk add libc-dev && apk add libffi-dev

RUN apk update && apk add cmake 

COPY requirements.txt requirements.txt

RUN apk add --no-cache git

RUN /usr/local/bin/python3.10 -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt 

# Cmake is a dependency for building libgit2

RUN apk update && apk add bash

COPY . .

EXPOSE 3000

CMD [ "python3", "launcher.py" ]