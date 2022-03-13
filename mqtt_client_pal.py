import paho.mqtt.client
import json
import sys
import time
from config import Constants

sys.path.append('../PAL_Script/MNLib/')
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
    global connected
    topic = 'unset'
    client = paho.mqtt.client.Client()

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
            if data ['PALID'] == 2:
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
    del PAL

    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()
