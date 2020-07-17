FROM python:3.7
#could use the prebuild python images instead

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

RUN python3 mbta.py

RUN python3 test.py

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]