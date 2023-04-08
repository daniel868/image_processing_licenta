from kafka import KafkaProducer, KafkaConsumer
from AddVideoEffects import AddVideoEffects
import cv2
import json
import threading

# dev_kafka_server = 'localhost:9092'
prod_kafka_server = '192.168.1.136:9092'

start_stop_topic = 'startstoptopic'
videotopic = 'demotopic'
videoEffects = AddVideoEffects()

is_streaming = False


def serializer(message):
    return json.dumps(message).encode('utf-8')


class VideoProducer:
    def __init__(self):
        self.kafkaProducer = KafkaProducer(
            bootstrap_servers=prod_kafka_server,
            key_serializer=serializer
        )
        self.kafkaStartStopConsumer = KafkaConsumer(
            start_stop_topic,
            bootstrap_servers=prod_kafka_server,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.startStopThread = threading.Thread(target=self.start_stop_streaming)
        self.startStopThread.start()

        self.streamingThread = threading.Thread(target=self.start_streaming)
        self.streamingThread.start()

    def start_streaming(self):
        camera = cv2.VideoCapture(0)
        print('Start Streaming')

        while True:
            if is_streaming:
                success, frame = camera.read()
                if success:
                    self.process_flux(frame)
                else:
                    print('Could not capture current frame')

    def process_flux(self, frame):
        processFrame = videoEffects.processGrayscaleFrame(frame)
        ret, buffer = cv2.imencode('.jpg', processFrame)
        self.sent_process_image(buffer)

    def sent_process_image(self, buffer):
        self.kafkaProducer.send(videotopic, key='key_message', value=buffer.tobytes())

    def start_stop_streaming(self):
        for msg in self.kafkaStartStopConsumer:
            print('Receivend value: ' + str(msg.value))
            global is_streaming
            is_streaming = msg.value['status'] == 'START_STREAMING'


if __name__ == '__main__':
    videoProducer = VideoProducer()
