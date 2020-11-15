FROM python:3.8

RUN mkdir /bulbe

WORKDIR /bulbe

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY src /bulbe
COPY config /config
COPY auth /auth


ENTRYPOINT ["python3", "launcher.py"]