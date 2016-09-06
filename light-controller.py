#! /usr/bin/env python

import sys
import json
import pika

sys.path.insert(0, './lib/arduinoserial')
import arduinoserial

print('Iceberg Light Controller')

if not len(sys.argv) > 3:
    print('Usage: ./light-controller.py [iceberg id] [serial port] [baudrate]')
    sys.exit(1)

icebergId = sys.argv[1];
serialPort = sys.argv[2];
baudrate = sys.argv[3];

arduino = arduinoserial.SerialPort(serialPort, baudrate)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='events', type='topic')
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='events', queue=queue_name, routing_key=('{}.#.touch.event'.format(icebergId)));
channel.queue_bind(exchange='events', queue=queue_name, routing_key=('{}.proximity.event'.format(icebergId)));
channel.queue_bind(exchange='events', queue=queue_name, routing_key='#.correspondence.event');

def callback(channel, method, properties, body) :

    event = json.loads(body);

    if event['type'] == 'MULTI_BERG':
        #print("facet:{0}:{1}".format(event['sensorNumber'], 2))
        arduino.write("facet:{0}:{1}".format(event['sensorNumber'], 2));

    if event['type'] == 'TOUCH':
        #print("facet:{0}:{1}".format(event['sensorNumber'], (1 if event['touched'] else 0)))
        arduino.write("facet:{0}:{1}".format(event['sensorNumber'], (1 if event['touched'] else 0)));

    if event['type'] == 'PROXIMITY':
        #print("facet:{0}:{1}".format(event['sensorNumber'], (1 if event['touched'] else 0)))
        arduino.write("facet:{0}:{1}".format(6, (1 if event['personPresent'] else 0)));

channel.basic_consume(callback, queue=queue_name, no_ack=True)
channel.start_consuming()
