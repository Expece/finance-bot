FROM python:3.10

WORKDIR /home

RUN apt-get update -qy
RUN apt-get install -qy python3-pip

COPY . ./

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]