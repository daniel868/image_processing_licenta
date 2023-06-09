import threading
import json
from kafka import KafkaConsumer
import time


video_topic = 'demotopic'
video_topic_png = 'demotopic_png'
auth_topic = 'authTopic'
start_stop_topic = 'start_stop_topic'
reading_topic = 'reading_topic'
metadata_reading_topic = 'metadata_reading_topic'


class KafkaService:
    def __init__(self, dev_kafka_server):
        self.dev_kafka_server = dev_kafka_server
        self.kafkaAuthConsumer = KafkaConsumer(
            auth_topic,
            bootstrap_servers=dev_kafka_server,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.metadataConsumer = KafkaConsumer(
            metadata_reading_topic,
            bootstrap_servers=dev_kafka_server,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.authThreadConsumer = threading.Thread(target=self.consume_auth_credential)
        self.authThreadConsumer.start()
        self.user_token = ''
        self.user_name = ''
        self.fps = 0
        self.metadata = {}

    def serializer(message):
        return json.dumps(message).encode('utf-8')

    def produce_video_stream(self):
        consumer = KafkaConsumer(
            video_topic,
            bootstrap_servers=self.dev_kafka_server
        )
        print('Start consuming JPG Frames')
        for msg in consumer:
            yield (b' --frame\r\n' b'Content-type: imgae/jpeg\r\n\r\n' + msg.value + b'\r\n')

    def produce_png_stream(self):
        consumer = KafkaConsumer(
            video_topic_png,
            bootstrap_servers=self.dev_kafka_server
        )

        print('Start consuming PNG frame')
        for msg in consumer:
            yield (b' --frame\r\n' b'Content-type: imgae/png\r\n\r\n' + msg.value + b'\r\n')

    def consume_auth_credential(self):
        for message in self.kafkaAuthConsumer:
            print('Receivend value: ' + str(message.value))
            self.user_token = message.value['token']
            self.user_name = message.value['username']

    def read_file_stream(self):
        consumer = KafkaConsumer(
            reading_topic,
            bootstrap_servers=self.dev_kafka_server
        )
        start_time = time.time()
        frames = 0
        print('Start reading')
        for msg in consumer:
            end_time = time.time()
            frames = frames + 1
            fps = frames / (end_time - start_time)
            self.fps = fps
            print('Frame arrived: FPS: ' + str(fps))
            yield (b' --frame\r\n' b'Content-type: imgae/jpeg\r\n\r\n' + msg.value + b'\r\n')
