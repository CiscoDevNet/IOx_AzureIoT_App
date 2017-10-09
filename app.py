import paho.mqtt.client as mqtt
import cred_gen as Creds
import config as config
import json

# Setting up Data Sync Broker Details
MQTT = config.cfg.get("DataMQTTBroker", "ip_or_url")
MQTTPORT = int(config.cfg.get("DataMQTTBroker", "port"))

# Setting up Azure MQTT connection details
azure_sharedaccesskey = config.cfg.get("AzureCreds", "sharedAccessKey")
azure_client_id = config.cfg.get("AzureCreds", "deviceID")
IoTHub = config.cfg.get("AzureCreds", "HubName")
azure_mqtt_port = int(config.cfg.get("AzureCreds", "port"))

# Using the credentials generator to create proper credentials for Azure
creds = Creds.Creds(IoTHub, azure_client_id, azure_sharedaccesskey)

azure_topic = creds.hubTopicPublish

# Defining MQTT client for MQTT Generated Data
data_client = mqtt.Client()

# Defining Azure MQTT client for sending messages to Azure IoT Hub via MQTT
azure_mqtt_client = mqtt.Client(azure_client_id, mqtt.MQTTv311)
azure_mqtt_client.username_pw_set(creds.hubUser, creds.generate_sas_token(creds.endpoint, azure_sharedaccesskey))
azure_mqtt_client.tls_set(config.cfg.get("CertLocation", "alpine"))


def data_on_connect(client, userdata, flags, rc):
    print("Connected with result " + str(rc) + ". Data Broker Connection")

    client.subscribe("IOx")


def azure_on_connect(client, userdata, flags, rc):
    print("Connected with result " + str(rc) + ". Azure MQTT Connection")
    azure_mqtt_client.subscribe(azure_topic)


def azure_on_publish(client, userdata, msg):
    print("Azure Message Published")


def data_on_message(client, userdata, msg):
    mess = msg.payload.decode('utf-8')
    print(mess)
    read_mess = mess.split(",")
    device_mess = str(read_mess[0])
    device_dict = json.loads(device_mess)
    if device_dict["light-on"] == True:
        azure_mqtt_client.publish(azure_topic, mess)
    else:
        print("No Azure Messages Sent")


def azure_on_message(client, userdata, msg):
    mess = msg.payload.decode('utf-8')
    print(mess)


data_client.on_connect = data_on_connect
data_client.on_message = data_on_message
data_client.connect(MQTT, MQTTPORT, 60)

azure_mqtt_client.connect(IoTHub, azure_mqtt_port, 60)
azure_mqtt_client.on_message = azure_on_message
azure_mqtt_client.on_connect = azure_on_connect
azure_mqtt_client.on_publish = azure_on_publish
azure_mqtt_client.loop_start()

data_client.loop_forever()
