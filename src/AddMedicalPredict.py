from kafka import KafkaConsumer, KafkaProducer
import cv2
import numpy as np
from keras.models import load_model
import threading
import json

medical_predict_topic = "medical_topic"
medical_producer = "medical_producer_topic"
dev_kafka_server = 'localhost:9092'
prod_kafka_server = 'localhost:9092'

# define parameters for model processing
img_rows, img_cols = 28, 28
num_classes = 7
nb_lstm = 64
nb_time_steps = img_rows
dim_input_vector = img_cols

skin_diseases = ['akiec',
                 'bcc',
                 'bkl',
                 'df',
                 'mel',
                 'nv',
                 'vasc'
                 ]


def serializer(message):
    return json.dumps(message).encode('utf-8')


class AddMedicalPredict:
    def __init__(self):
        self.medical_predict_consumer = KafkaConsumer(
            medical_predict_topic,
            bootstrap_servers=dev_kafka_server
        )
        self.medical_predict_producer = KafkaProducer(
            bootstrap_servers=dev_kafka_server,
            key_serializer=serializer,
            value_serializer=serializer
        )
        self.med_prediction = {}

        self.medicalThreadConsumer = threading.Thread(target=self.subscribe_to_consumer)
        self.model = load_model('final_model.h5')
        self.medicalThreadConsumer.start()

    def subscribe_to_consumer(self):
        for message in self.medical_predict_consumer:
            print('start medical predict')
            frame = cv2.imdecode(np.fromstring(message.value, dtype=np.uint8), cv2.IMREAD_COLOR)
            self.process_frames(frame)

    def process_frames(self, frame):
        # Convert the frame to grayscale

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Resize the image to the required input size of the model
        img = cv2.resize(gray, (img_cols, img_rows))

        # Reshape the image to fit the input shape of the model
        img = np.reshape(img, (1, nb_time_steps, dim_input_vector))

        img = np.expand_dims(img, axis=3)
        img = np.repeat(img, 3, axis=3)

        prediction = self.model.predict(img)

        value = sum(prediction[0, :])

        self.med_prediction = self.calculate_class_probabilities(prediction[0, :], value)
        self.medical_predict_producer.send(medical_producer, self.med_prediction)

    def calculate_class_probabilities(self, prediction, sum):
        max_class = {}

        percent_array_values = [
            prediction[i] / sum * 100 for i in range(len(prediction))
        ]

        max_value = max(percent_array_values)
        max_class['maxValue'] = round(max_value, 2)

        for i in range(len(prediction)):
            max_class[skin_diseases[i]] = round(percent_array_values[i], 2)

        return max_class
