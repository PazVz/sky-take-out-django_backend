FROM python:3.12

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN wget https://github.com/apache/rocketmq-client-cpp/releases/download/2.2.0/rocketmq-client-cpp-2.2.0.amd64.deb && \
    dpkg -i rocketmq-client-cpp-2.2.0.amd64.deb && \
    apt-get install -f -y

RUN pip install -r requirements.txt

COPY . /code/