import cv2


class AddVideoEffects():

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

    def processJPG_80(self, frame):
        jpeg_quality = 80
        jpeg_params = [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality]
        ret, frame_jpeg_80 = cv2.imencode('.jpg', frame, jpeg_params)
        decompressed_frame = cv2.imdecode(frame_jpeg_80, cv2.IMREAD_COLOR)

        return decompressed_frame
