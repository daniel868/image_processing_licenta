import cv2


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
        effectFrame = self.applyEffect(frame,streaming_info['effectType'])
        if streaming_info['compressionLevel'] != -1:
            jpeg_params = [cv2.IMWRITE_JPEG_QUALITY, streaming_info['compressionLevel']]
            ret, frame_jpeg = cv2.imencode('.jpg', effectFrame, jpeg_params)
        else:
            ret, frame_jpeg = cv2.imencode('.jpg', effectFrame)
        return frame_jpeg

    def processPNG(self, frame, streaming_info):
        effectFrame = self.applyEffect(frame, streaming_info['effectType'])
        if streaming_info['compressionLevel'] != -1:
            png_params = [cv2.IMWRITE_PNG_COMPRESSION, streaming_info['compressionLevel']]
            ret, frame_png = cv2.imencode('.png', effectFrame, png_params)
        else:
            ret, frame_png = cv2.imencode('.png', effectFrame)

        return frame_png

    def applyEffect(self, frame, effect_type):
        if 'GRAYSCALE' == effect_type:
            return self.processGrayscaleFrame(frame)
        if 'RGB' == effect_type:
            return self.processRgbFrame(frame)
        if 'HSV' == effect_type:
            return self.processHsvFrame(frame)
        return frame
