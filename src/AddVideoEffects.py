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
        effect_frame = self.applyEffect(frame,streaming_info['effectType'])
        if streaming_info['compressionLevel'] != -1:
            jpeg_params = [cv2.IMWRITE_JPEG_QUALITY, streaming_info['compressionLevel']]
            ret, frame_jpeg = cv2.imencode('.jpg', effect_frame, jpeg_params)
        else:
            ret, frame_jpeg = cv2.imencode('.jpg', effect_frame)
        return [frame_jpeg, effect_frame]

    def processPNG(self, frame, streaming_info):
        effect_frame = self.applyEffect(frame, streaming_info['effectType'])
        if streaming_info['compressionLevel'] != -1:
            png_params = [cv2.IMWRITE_PNG_COMPRESSION, streaming_info['compressionLevel']]
            ret, frame_png = cv2.imencode('.png', effect_frame, png_params)
        else:
            ret, frame_png = cv2.imencode('.png', effect_frame)

        return [frame_png, effect_frame]

    def applyEffect(self, frame, effect_type):
        if 'GRAYSCALE' == effect_type:
            return self.processGrayscaleFrame(frame)
        if 'RGB' == effect_type:
            return self.processRgbFrame(frame)
        if 'HSV' == effect_type:
            return self.processHsvFrame(frame)
        return frame
