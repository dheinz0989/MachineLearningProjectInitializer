
FROM python:3.8
MAINTAINER Dominik Heinz "dheinz0989@gmail.com"
RUN apt-get update     && apt-get --yes install g++     && apt-get clean
WORKDIR /app
COPY requirements.txt /app
COPY src /app 
RUN pip install -r requirements.txt
CMD ["python", "app.py" ]
        