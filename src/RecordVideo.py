import cv2

file_name = None
codec = None
out_mp4 = None
camera = cv2.VideoCapture(0)
frame_per_second = int(camera.get(cv2.CAP_PROP_FPS))
frame_size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
              int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
isFinishWriting = False


class RecordVideo:
    def init_write_file(self, properties_dict):
        global file_name
        file_name = properties_dict['file_name'] + '.' + properties_dict['file_extension']
        global codec
        codec = cv2.VideoWriter_fourcc(*'mp4v')
        global out_mp4
        custom_video_encoder_type = self.get_video_encoder_type(properties_dict)
        if custom_video_encoder_type is not None:
            out_mp4 = cv2.VideoWriter(file_name, codec, frame_per_second, frame_size, custom_video_encoder_type)
        else:
            out_mp4 = cv2.VideoWriter(file_name, codec, frame_per_second, frame_size)
        global isFinishWriting
        isFinishWriting = False

    def clear_write_file(self):
        global out_mp4
        global file_name
        global codec
        global isFinishWriting
        if out_mp4:
            out_mp4.release()
            out_mp4 = None
        file_name = None
        codec = None

    def write_file(self, properties_dict, frame):
        global out_mp4
        if 'START_WRITE' == properties_dict['write_status']:
            if out_mp4 is None:
                print('Initialize first')
                self.init_write_file(properties_dict)
            if out_mp4:
                print('Writing frame on hard-disk with frame length: ' + str(len(frame)))
                out_mp4.write(frame)

        global isFinishWriting
        if 'STOP_WRITE' == properties_dict['write_status'] and not isFinishWriting:
            print('Finishing saving to disk')
            isFinishWriting = True
            self.clear_write_file()

    def get_video_encoder_type(self, properties_dict):
        if 'GRAYSCALE' == properties_dict['effectType']:
            return 0
        if 'RGB' == properties_dict['effectType'] or 'HSV' == properties_dict['effectType']:
            return 1

        return None
