FROM python:alpine
RUN mkdir /database
RUN mkdir -p /libs/utils
RUN pip install flask paho-mqtt pymongo
COPY . /database
COPY ../libs/utils /libs/utils
WORKDIR /database
