import cv2
import numpy as np
from keras.models import load_model

# Load the pre-trained model
model = load_model('final_model.h5')

# Parameters for MNIST dataset
img_rows, img_cols = 28, 28
num_classes = 7

# Parameters for LSTM network
nb_lstm = 64
nb_time_steps = img_rows
dim_input_vector = img_cols


# Initialize the camera
# cap = cv2.VideoCapture(0)

# Set the camera resolution
# cap.set(3, 640)
# cap.set(4, 480)

# frame = cv2.imread('ISIC_0024329.jpg')
# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# rgb = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
# Resize the image to the required input size of the model
# img = cv2.resize(rgb, (img_cols, img_rows))

# Reshape the image to fit the input shape of the model
# img = np.reshape(img, (1, nb_time_steps, dim_input_vector))

# Normalize the image
# img = (img - np.mean(img)) / np.std(img)
# img = np.expand_dims(img, axis=3)
# img = np.repeat(img, 3, axis=3)
# Predict the label of the image
# prediction = model.predict(img)
# print(str(prediction))
# Get the predicted class label
# label = np.argmax(prediction)

# Print the predicted label on the frame
# cv2.putText(frame, 'Prediction: ' + str(label), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
# print('Prediction: ' + str(label))
# Display the frame
# cv2.imshow('Camera', frame)
def build_percent_function(prediction, sum):
    max_class = {}

    percent_array_values = [
        prediction[0] / sum * 100,
        prediction[1] / sum * 100,
        prediction[2] / sum * 100,
        prediction[3] / sum * 100,
        prediction[4] / sum * 100,
        prediction[5] / sum * 100,
        prediction[6] / sum * 100,
    ]

    max_value = max(percent_array_values)
    max_class[0] = max_value
    max_class[1] = percent_array_values[0]
    max_class[2] = percent_array_values[1]
    max_class[3] = percent_array_values[2]
    max_class[4] = percent_array_values[3]
    max_class[5] = percent_array_values[4]
    max_class[6] = percent_array_values[5]
    max_class[7] = percent_array_values[6]

    return max_class


def format_dict(my_dict):
    output = ""
    for key, value in my_dict.items():
        output += f"{key}:{round(value, 2)}%\n"
    return output


cap = cv2.VideoCapture(1)
while True:
    # Capture the frame from the camera
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Resize the image to the required input size of the model
    img = cv2.resize(gray, (img_cols, img_rows))

    # Reshape the image to fit the input shape of the model
    img = np.reshape(img, (1, nb_time_steps, dim_input_vector))
    #
    # # Normalize the image
    # img = (img - np.mean(img)) / np.std(img)
    # img = (img - np.mean(img)) / np.std(img)
    img = np.expand_dims(img, axis=3)
    img = np.repeat(img, 3, axis=3)

    # Predict the label of the image
    prediction = model.predict(img)

    # Get the predicted class label
    # print(prediction)
    value = sum(prediction[0, :])
    out_dict = build_percent_function(prediction[0, :], value)
    print(out_dict)
    # print("Sum is:" + str(value))
    label = np.argmax(prediction)
    output_string = format_dict(out_dict)
    print(output_string)
    # Print the predicted label on the frame
    # cv2.putText(frame, 'Prediction: ' + label, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the frame
    # cv2.imshow('Camera', frame)

    # Wait for key press
    # k = cv2.waitKey(1)

    # Exit the loop on 'q' key press
    # if k == ord('q'):
    #     break

# Release the camera and destroy all windows
# cap.release()
# cv2.destroyAllWindows()
