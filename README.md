# iiot-poc-template

## Dependencies
freeopcua
pymodbus
mosquito
paho-mqtt
python-etcd (maybe not)

## install mosquito client
sudo apt-get install mosquitto

## Install mongodb
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.2.list

sudo apt update

sudo apt-get install -y mongodb
