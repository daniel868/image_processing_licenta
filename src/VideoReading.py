import cv2
import threading
import json
from kafka import KafkaProducer, KafkaConsumer
import time

reading_topic = 'reading_topic'
start_reading_topic = 'start_reading_topic'
global current_frame
current_frame = 0
global is_reading
is_reading = False
global file_path
global from_zero
from_zero = None


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

    def start_stop_reading(self):
        global is_reading, file_path, from_zero
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

    def read_chucked_frames(self):
        global current_frame, is_reading, file_path, from_zero
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

                # while start_frame < total_frames and is_reading:
                #     # Set the frame position to the start frame
                #     cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                #
                #     # Read the frames in the current chunk
                #     for i in range(start_frame, end_frame):
                #         if not is_reading:
                #             # pause the video
                #             break
                #         ret, frame = cap.read()
                #         current_frame = i
                #         if not ret:
                #             break
                #         # Do something with the frame, for example, display it
                #         # cv2.imshow('frame', frame)
                #         ret, frame_jpeg = cv2.imencode('.jpg', frame)
                #         if ret:
                #             self.readerProducer.send(reading_topic, key='key_reader_frame', value=frame_jpeg.tobytes())
                #         print('Current frame count: ' + str(current_frame))
                #         if current_frame == (total_frames - 1):
                #             is_reading = False
                #             print('Video Ended')
                #     # cv2.waitKey(25)
                #
                #     # Set the start and end frames for the next chunk
                #     start_frame = end_frame
                #     end_frame = min(start_frame + chunk_size, total_frames)
