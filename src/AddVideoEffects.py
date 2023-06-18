import cv2

haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")


class AddVideoEffects:

    def processGrayscaleFrame(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def processRgbFrame(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def processHsvFrame(self, frame):
        rgbFrame = self.processRgbFrame(frame)
        hsvFrame = cv2.cvtColor(rgbFrame, cv2.COLOR_BGR2HSV)
        rgbFrame[:, :, 0], rgbFrame[:, :, 1], rgbFrame[:, :, 2] = hsvFrame[:, :, 2], hsvFrame[:, :, 1], hsvFrame[:, :,
                                                                                                        0]
        return rgbFrame

    def processJPG(self, frame, streaming_info):
        try:
            effect_frame = self.applyEffect(frame, streaming_info['effectType'])
            if streaming_info['compressionLevel'] != -1:
                jpeg_params = [cv2.IMWRITE_JPEG_QUALITY, streaming_info['compressionLevel']]
                ret, frame_jpeg = cv2.imencode('.jpg', effect_frame, jpeg_params)
            else:
                jpeg_params = [cv2.IMWRITE_JPEG_QUALITY, 50]
                ret, frame_jpeg = cv2.imencode('.jpg', effect_frame, jpeg_params)
            return [frame_jpeg, effect_frame]
        except Exception as e:
            ret, frame_jpeg = cv2.imencode('.jpg', frame)
            return [frame_jpeg, frame]

    def processPNG(self, frame, streaming_info):
        effect_frame = self.applyEffect(frame, streaming_info['effectType'])
        if streaming_info['compressionLevel'] != -1:
            png_params = [cv2.IMWRITE_PNG_COMPRESSION, streaming_info['compressionLevel']]
            ret, frame_png = cv2.imencode('.png', effect_frame, png_params)
        else:
            png_params = [cv2.IMWRITE_PNG_COMPRESSION, 50]
            ret, frame_png = cv2.imencode('.png', effect_frame, png_params)

        return [frame_png, effect_frame]

    def process_eyes_recognition(self, frame):
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        face_rect = haar_cascade.detectMultiScale(frame, 1.1, 9)

        for (x, y, w, h) in face_rect:
            roi_gray = gray_img[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]

            eyes = eye_cascade.detectMultiScale(roi_gray)

            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

            frame = roi_color

        return frame

    def process_face_recognition(self, frame):
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        face_rect = haar_cascade.detectMultiScale(gray_img, 1.1, 9)

        for (x, y, w, h) in face_rect:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return frame

    def applyEffect(self, frame, effect_type):
        if 'GRAYSCALE' == effect_type:
            return self.processGrayscaleFrame(frame)
        if 'RGB' == effect_type:
            return self.processRgbFrame(frame)
        if 'HSV' == effect_type:
            return self.processHsvFrame(frame)
        if 'Facial recognition' == effect_type:
            return self.process_face_recognition(frame)
        if 'Eyes recognition' == effect_type:
            return self.process_eyes_recognition(frame)
        return frame
