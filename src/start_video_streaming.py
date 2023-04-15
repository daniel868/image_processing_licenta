from kafka import KafkaProducer, KafkaConsumer
from AddVideoEffects import AddVideoEffects
import cv2
import json
import threading

dev_kafka_server = 'localhost:9092'
#prod_kafka_server = '192.168.1.136:9092'

start_stop_topic = 'startstoptopic'
videotopic = 'demotopic'
video_topic_png = 'demotopic_png'
videoEffects = AddVideoEffects()

is_streaming = False
streaming_info = {}


def serializer(message):
    return json.dumps(message).encode('utf-8')


class VideoProducer:
    def __init__(self):
        self.kafkaProducer = KafkaProducer(
            bootstrap_servers=dev_kafka_server,
            key_serializer=serializer
        )
        self.kafkaStartStopConsumer = KafkaConsumer(
            start_stop_topic,
            bootstrap_servers=dev_kafka_server,
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
                    if 'JPG' == streaming_info['videoFormat']:
                        self.process_jpg_flux(frame)
                    else:
                        self.process_png_flux(frame)
                else:
                    print('Could not capture current frame')

    def process_jpg_flux(self, frame):
        processFrame = videoEffects.processJPG(frame, streaming_info)
        self.sent_process_image(processFrame, videotopic)

    def process_png_flux(self, frame):
        processFrame = videoEffects.processPNG(frame, streaming_info)
        self.sent_process_image(processFrame, video_topic_png)

    def sent_process_image(self, buffer, topic):
        memory_kb = buffer.nbytes / 1024
        print('Memory used by the frame (KB):', memory_kb)
        self.kafkaProducer.send(topic, key='key_message', value=buffer.tobytes())

    def start_stop_streaming(self):
        for msg in self.kafkaStartStopConsumer:
            print('Receivend value: ' + str(msg.value))
            global is_streaming
            is_streaming = msg.value['status'] == 'START_STREAMING'
            global streaming_info
            streaming_info['videoFormat'] = msg.value['videoFormat']
            streaming_info['compressionLevel'] = msg.value['effects']['compressionLevel']
            streaming_info['effectType'] = msg.value['effects']['effectType']


if __name__ == '__main__':
    videoProducer = VideoProducer()
