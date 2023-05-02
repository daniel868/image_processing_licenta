import cv2
import threading
import json
from kafka import KafkaProducer, KafkaConsumer
import time
import os

reading_topic = 'reading_topic'
start_reading_topic = 'start_reading_topic'
metadata_reading_topic = 'metadata_reading_topic'
global current_frame
current_frame = 0
global is_reading
is_reading = False
global file_path
global from_zero
from_zero = None
global is_loading_metadata
is_loading_metadata = False
global folder_path
folder_path = ''


def serializer(message):
    return json.dumps(message).encode('utf-8')


class VideoReading:
    def __init__(self, kafka_server):
        self.kafka_server = kafka_server
        self.readerProducer = KafkaProducer(
            bootstrap_servers=self.kafka_server,
            key_serializer=serializer
        )
        self.event = threading.Event()
        self.startReaderConsumer = KafkaConsumer(
            start_reading_topic,
            bootstrap_servers=self.kafka_server,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.start_reading_thread = threading.Thread(target=self.start_stop_reading)
        self.start_reading_thread.start()

        self.reading_thread = threading.Thread(target=self.read_chucked_frames)
        self.reading_thread.start()

        self.videoInfoProducer = KafkaProducer(
            bootstrap_servers=self.kafka_server,
            key_serializer=serializer,
            value_serializer=serializer
        )

    def start_stop_reading(self):
        global is_reading, file_path, from_zero, is_loading_metadata, folder_path
        for msg in self.startReaderConsumer:
            print('Reading message arrived: ' + str(msg.value))
            if msg.value['readingStatus'] == 'START_READING':
                is_reading = True
                file_path = msg.value['filePath']
                from_zero = None
                if 'fromZero' in msg.value:
                    from_zero = msg.value['fromZero']

            if msg.value['readingStatus'] == 'STOP_READING':
                is_reading = False
                print('is_reading: ' + str(is_reading))

            if msg.value['readingStatus'] == 'METADATA_READING':
                is_loading_metadata = True
                folder_path = msg.value['folderPath']

    def read_chucked_frames(self):
        global current_frame, is_reading, file_path, from_zero, is_loading_metadata
        total_frame_count = 0
        start_time = time.time()
        while True:
            if is_reading:
                print('is_reading: ' + str(is_reading))
                cap = cv2.VideoCapture(file_path)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

                start_frame = 0 if from_zero is not None else current_frame
                chunk_size = 100
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

                for i in range(start_frame, total_frames):
                    if not is_reading:
                        # pause the video
                        break
                    ret, frame = cap.read()
                    current_frame = i

                    if not ret:
                        break
                    ret, frame_jpeg = cv2.imencode('.jpg', frame)
                    total_frame_count += 1
                    if ret:
                        # TODO: compute here FPS
                        end_time = time.time()
                        FPS = total_frame_count / (end_time - start_time)
                        print('FPS: ' + str(FPS))
                        self.readerProducer.send(reading_topic, key='key_reader_frame', value=frame_jpeg.tobytes())
                    if current_frame == (total_frames - 1):
                        is_reading = False
                        print('Video Ended')

            if is_loading_metadata:
                print('Loading metadata')
                file_paths = []
                var = (os.walk(folder_path))

                for root, directories, files in os.walk(folder_path):
                    for filename in files:
                        if filename.endswith('.mp4'):
                            file_path = os.path.join(root, filename)
                            file_paths.append(file_path)

                file_info = {}
                file_info['video_paths'] = file_paths
                print('Sending data: '+str(file_info))
                self.videoInfoProducer.send(metadata_reading_topic, key='metadata_key', value=file_info)
                is_loading_metadata = False
