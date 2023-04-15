import threading
import json
from kafka import KafkaConsumer, KafkaProducer

dev_kafka_server = 'localhost:9092'
video_topic = 'demotopic'
video_topic_png = 'demotopic_png'
auth_topic = 'authTopic'
start_stop_topic = 'start_stop_topic'

#prod_kafka_server = '192.168.1.136:9092'


class KafkaService:
    def __init__(self):
        self.kafkaAuthConsumer = KafkaConsumer(
            auth_topic,
            bootstrap_servers=dev_kafka_server,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.authThreadConsumer = threading.Thread(target=self.consume_auth_credential)
        self.authThreadConsumer.start()
        self.user_token = ''
        self.user_name = ''

    def serializer(message):
        return json.dumps(message).encode('utf-8')

    def produce_video_stream(self):
        consumer = KafkaConsumer(
            video_topic,
            bootstrap_servers=dev_kafka_server
        )
        print('Start consuming')
        for msg in consumer:
            print('Showing new frame')
            yield (b' --frame\r\n' b'Content-type: imgae/jpeg\r\n\r\n' + msg.value + b'\r\n')


    def produce_png_stream(self):
        consumer = KafkaConsumer(
            video_topic_png,
            bootstrap_servers=dev_kafka_server
        )

        print('Start consuming PNG frame')
        for msg in consumer:
            print('Streaming PNG frame')
            yield (b' --frame\r\n' b'Content-type: imgae/png\r\n\r\n' + msg.value + b'\r\n')

    def consume_auth_credential(self):
        for message in self.kafkaAuthConsumer:
            print('Receivend value: ' + str(message.value))
            self.user_token = message.value['token']
            self.user_name = message.value['username']
