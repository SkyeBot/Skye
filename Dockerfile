FROM python:3.9-alpine
RUN apk add --no-cache linux-headers && apk --no-cache add gcc musl-dev && apk add libc-dev && apk add libffi-dev

COPY requirements.txt requirements.txt

RUN apk add python3-dev

RUN apk add --no-cache git

RUN apk update
RUN apk add wget

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt 

# Cmake is a dependency for building libgit2



COPY . .

EXPOSE 2300

CMD [ "python3", "launcher.py" ]