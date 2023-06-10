import cv2
import json

file_name = None
codec = None
out_mp4 = None
isFinishWriting = False


class RecordVideo:
    def __init__(self, frame_per_second, frame_size):
        self.frame_per_second = frame_per_second
        self.frame_size = frame_size

    def init_write_file(self, properties_dict):
        global file_name
        # file_name = properties_dict['file_name'] + '.' + properties_dict['file_extension']
        file_name = properties_dict['file_name'] + '.mp4'
        global codec
        codec = cv2.VideoWriter_fourcc(*'mp4v')
        # codec = cv2.VideoWriter_fourcc(*'RGBA')
        global out_mp4
        custom_video_encoder_type = self.get_video_encoder_type(properties_dict)
        if custom_video_encoder_type is not None:
            out_mp4 = cv2.VideoWriter(file_name, codec, self.frame_per_second, self.frame_size,
                                      custom_video_encoder_type)
        else:
            out_mp4 = cv2.VideoWriter(file_name, codec, self.frame_per_second, self.frame_size)
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
            self.add_into_json_file(properties_dict['base_path'],
                                    properties_dict['file_name'],
                                    properties_dict['user_id'])

    def add_into_json_file(self, base_path, movie_name, movie_user_id):
        json_file_path = "src\\videos.json"
        windows_delimiter = '\\'
        linux_delimiter = '/'
        delimiter = linux_delimiter if linux_delimiter in base_path else windows_delimiter
        path_to_add = base_path + delimiter + movie_name + ".mp4"

        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)

        added = False

        for item in data:
            user_id = item['userId']

            if user_id == movie_user_id:
                current_videos_paths = item['videosPaths']
                new_movie_path = {"path_name": path_to_add}
                print('Added new movie to user: ' + str(movie_user_id) + ' ' + str(new_movie_path))
                current_videos_paths.append(new_movie_path)
                added = True
            break

        if added is not True:
            # add a new user object type
            print('Add a new object user')
            user_movie_data = {
                "userId": movie_user_id,
                "videosPaths": [
                    {
                        "path_name": path_to_add
                    }
                ]
            }
            data.append(user_movie_data)

        with open(json_file_path, "w") as json_file:
            json.dump(data, json_file)

    def get_video_encoder_type(self, properties_dict):
        if 'GRAYSCALE' == properties_dict['effectType']:
            return 0
        if 'RGB' == properties_dict['effectType'] or 'HSV' == properties_dict['effectType']:
            return 1

        return None
