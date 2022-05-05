import paho.mqtt.client
import json
import sys
import time
from config import Constants

sys.path.append(Constants.SCRIPTDIR + '../PAL_Script/MNLib/')

from apppal import AppPAL

connected  = False


def onConnect(client, userdata, flag, rc):
    global connected
    if rc == 0:
        connected = True
    else:
        print('failure to connect')
        exit

def main():
    AMBIENT_SENSE_PAL = 0x2
    TWELITE_ARIA = 0x6
    
    global connected
    topic = 'unset'
    client = paho.mqtt.client.Client(client_id="home_sensor")

    client.tls_set(
        ca_certs = Constants.ROOTCA,
        certfile = Constants.CERT,
        keyfile = Constants.PRIVATEKEY
    )

    client.on_connect = onConnect
    client.connect(Constants.ENDPOINT, port=Constants.PORT)
    client.loop_start()

    while not connected:
        pass

    PAL = AppPAL(port = Constants.COMPORT)

    while True:
        if PAL.ReadSensorData():
            data = PAL.GetDataDict()
            if data ['PALID'] == AMBIENT_SENSE_PAL:
                topic = "sensor/" + "palamb{0:04d}".format(data['LogicalID']) + "/sensor_update"
                now = time.time()
                senddata = {
                    'device_name' : "palamb{0:04d}".format(data['LogicalID']),
                    'type' : "Envsensor",
                    'timestamp' : int(now),
                    'temperature' : data.get('Temperature'),
                    'humidity' : data.get('Humidity'),
                    'illuminance' : data.get('Illuminance'),
                    'power' : data.get('Power') 
                }
                print(topic, senddata)
                info = client.publish(topic, json.dumps(senddata))
                info.wait_for_publish()
            if data ['PALID'] == TWELITE_ARIA:
                topic = "sensor/" + "twelaria{0:04d}".format(data['LogicalID']) + "/sensor_update"
                now = time.time()
                senddata = {
                    'device_name' : "twelaria{0:04d}".format(data['LogicalID']),
                    'type' : "Envsensor",
                    'timestamp' : int(now),
                    'temperature' : data.get('Temperature'),
                    'humidity' : data.get('Humidity'),
                    'illuminance' : 0.0,
                    'power' : data.get('Power') 
                }
                print(topic, senddata)
                info = client.publish(topic, json.dumps(senddata))
                info.wait_for_publish()
 
    del PAL

    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()
