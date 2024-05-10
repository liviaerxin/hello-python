import requests
import os
import mimetypes

file_path = "/root/Documents/storage/files/xxx.mp4"
url = "http://127.0.0.1/api/v1/upload_videos"

mime_type, encoding = mimetypes.guess_type(file_path)
filename = os.path.basename(file_path)
# mime_type = "video/mp4"
# filename = "xxx.mp4"

form_data = {"station_to_station_id": 31, "is_baseline": True, "train_speed": 10}
files = {
    # "key": (filename, fileobj, content_type, custom_headers)
    "upload_file": (filename, open(file_path, "rb"), mime_type),
}


response = requests.post(url, files=files, data=form_data)

print(response.status_code)
print(response.content)