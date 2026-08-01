FROM python:3.12-slim

RUN mkdir /bulbe

WORKDIR /bulbe

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . /bulbe

ENTRYPOINT ["python3", "launcher.py"]