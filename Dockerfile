FROM python:alpine

RUN apk upgrade -v --available --no-cache \
    && apk add ca-certificates && pip install --no-cache-dir --upgrade pip setuptools wheel

WORKDIR /root/

COPY app.py .
COPY config.py .
COPY cred_gen.py .
COPY requirements.txt .
COPY package_config.ini .

RUN pip3 install -r requirements.txt

#IOx Labels
LABEL "cisco.cpuarch"="x86_64" \
      "cisco.resources.profile"="c1.small" \
      "cisco.resources.disk"="20" \
      "cisco.resources.network.0.interface-name"="eth0"

CMD ["python app.py"]