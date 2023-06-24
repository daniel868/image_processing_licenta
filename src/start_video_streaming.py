from kafka import KafkaProducer, KafkaConsumer
from AddVideoEffects import AddVideoEffects
from RecordVideo import RecordVideo
from VideoReading import VideoReading
import cv2
import json
import threading

dev_kafka_server = 'localhost:9092'

start_stop_topic = 'startstoptopic'
videotopic = 'demotopic'
video_topic_png = 'demotopic_png'
videoEffects = AddVideoEffects()
videoReading = VideoReading(dev_kafka_server)

is_streaming = False
streaming_info = {}
# camera = None

medical_predict_topic = "medical_topic"
is_running_medical_analyze = False

board_status_topic = "board_status_topic_request"
board_status_topic_result = "board_status_topic_result"


def serializer(message):
    return json.dumps(message).encode('utf-8')


class VideoProducer:
    def __init__(self, record_video):
        self.record_video = record_video
        self.kafkaProducer = KafkaProducer(
            bootstrap_servers=dev_kafka_server,
            key_serializer=serializer
        )
        self.kafkaStartStopConsumer = KafkaConsumer(
            start_stop_topic,
            bootstrap_servers=dev_kafka_server,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.kafkaMedFrameProducer = KafkaProducer(
            bootstrap_servers=dev_kafka_server,
            key_serializer=serializer
        )

        self.kafkaStatusConsumer = KafkaConsumer(
            board_status_topic,
            bootstrap_servers=dev_kafka_server,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        self.kafkaStatusProducer = KafkaProducer(
            bootstrap_servers=dev_kafka_server,
            key_serializer=serializer,
            value_serializer=serializer
        )

        self.startStopThread = threading.Thread(target=self.start_stop_streaming)
        self.startStopThread.start()

        self.streamingThread = threading.Thread(target=self.start_streaming)
        self.streamingThread.start()

        self.statusThread = threading.Thread(target=self.handle_board_status)
        self.statusThread.start()

    def start_streaming(self):
        # global camera
        camera = cv2.VideoCapture(0)
        print('Start Streaming')

        while True:
            if is_streaming and camera is not None:
                success, frame = camera.read()
                if success:
                    frame_to_write = None
                    if 'JPG' == streaming_info['videoFormat']:
                        frame_to_write = self.process_jpg_flux(frame)
                    else:
                        frame_to_write = self.process_png_flux(frame)

                    if ('START_WRITE' == streaming_info['write_status'] or
                            'STOP_WRITE' == streaming_info['write_status']):
                        self.record_video.write_file(streaming_info, frame_to_write)

                    if is_running_medical_analyze:
                        self.sent_medical_process_frame(frame)
                else:
                    print('Could not capture current frame')

    def process_jpg_flux(self, frame):
        [frame_jpeg, effect_frame] = videoEffects.processJPG(frame, streaming_info)
        self.sent_process_image(frame_jpeg, videotopic)
        return effect_frame

    def process_png_flux(self, frame):
        [frame_png, effect_frame] = videoEffects.processPNG(frame, streaming_info)
        self.sent_process_image(frame_png, video_topic_png)
        return effect_frame

    def sent_process_image(self, buffer, topic):
        memory_kb = buffer.nbytes / 1024
        # print('Memory used by the frame (KB):', memory_kb)
        self.kafkaProducer.send(topic, key='key_message', value=buffer.tobytes())

    def sent_medical_process_frame(self, camera_frame):
        frame_str = cv2.imencode('.jpg', camera_frame)[1].tostring()
        self.kafkaMedFrameProducer.send(medical_predict_topic, key='key_medical_frame', value=frame_str)

    def start_stop_streaming(self):
        for msg in self.kafkaStartStopConsumer:
            print('Receivend value: ' + str(msg.value))
            global is_streaming
            is_streaming = msg.value['status'] == 'START_STREAMING'
            global streaming_info
            streaming_info['videoFormat'] = msg.value['videoFormat']
            streaming_info['compressionLevel'] = msg.value['effects']['compressionLevel']
            streaming_info['effectType'] = msg.value['effects']['effectType']
            streaming_info['write_status'] = msg.value['saveFileProps']['writeStatus']
            streaming_info['file_name'] = msg.value['saveFileProps']['fileName']
            global is_running_medical_analyze
            is_running_medical_analyze = msg.value['effects']['medical_status'] == 'START_STREAMING'
            streaming_info['base_path'] = msg.value['folderPath']
            streaming_info['user_id'] = msg.value['userId']

    def handle_board_status(self):
        for msg in self.kafkaStatusConsumer:
            if msg is not None:
                file_info = {'status': 'connected'}
                print('Sending status update to web')
                self.kafkaStatusProducer.send(board_status_topic_result, key='status_update', value=file_info)


if __name__ == '__main__':
    camera = cv2.VideoCapture(0)
    frame_per_second = int(camera.get(cv2.CAP_PROP_FPS))
    frame_size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                  int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    recordVideo = RecordVideo(frame_per_second, frame_size)
    camera.release()
    videoProducer = VideoProducer(recordVideo)
