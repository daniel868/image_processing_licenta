import json
import os
from moviepy.editor import VideoFileClip

json_file_path = "videos.json"

with open(json_file_path, "r") as json_file:
    data = json.load(json_file)

for item in data:
    current_videos_paths = item['videosPaths']
    for item2 in current_videos_paths:
        path = item2['path_name']
        file_size = os.path.getsize(path) / (1024 * 1024)
        item2['file_size'] = format(file_size, ".2f")
        video = VideoFileClip(path)
        duration = video.duration
        item2['duration'] = str(duration)

with open(json_file_path, "w") as json_file:
    json.dump(data, json_file)
