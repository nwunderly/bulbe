FROM python:3.8

RUN mkdir /bulbe

WORKDIR /bulbe

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . /bulbe
COPY config /config

ENTRYPOINT ["python3", "launcher.py"]