FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    docker.io \
    python3 \
    python3-pip \
    curl \
    iputils-ping \
 && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip3 install -r requirements.txt


CMD [ "python3", "app.py" ]

EXPOSE 5000