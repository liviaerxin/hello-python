# https://stackoverflow.com/questions/12503368/making-a-video-with-opencv-and-ffmpeg-how-to-find-the-right-color-format
# https://stackoverflow.com/questions/34167691/pipe-opencv-images-to-ffmpeg-using-python
# pipe from python output to ffmpeg input
"""Usage
# pure ffmpeg
ffmpeg -i input.mp4 -c:v rawvideo -pix_fmt bgr24 -r 60 -f rawvideo pipe: | ffmpeg -y -f rawvideo -pix_fmt bgr24 -s 1920x1080 -r 60 -i pipe: -pix_fmt yuv420p -c:v h264_nvenc foo.mp4
ffmpeg -i input.mp4 -pix_fmt yuv420p -r 60 -f rawvideo pipe: | ffmpeg -y -f rawvideo -pix_fmt yuv420p -s 1920x1080 -r 60 -i pipe: -c:v h264_nvenc foo.mp4
ffmpeg -i input.mp4 -an -f h264 pipe: | ffmpeg -y -f h264 -i pipe: -c:v h264_nvenc foo.mp4

# video_size must be same with the output from python
# OSX GPU
python opencv_pipe_ffmpeg_cmd.py | ffmpeg -y -f rawvideo -pix_fmt bgr24 -s 1920x1080 -r 60 -an -i pipe: -r 60 -c:v h264_videotoolbox foo.mp4

# NVIDIA GPU
python opencv_pipe_ffmpeg_cmd.py | ffmpeg -y -f rawvideo -pix_fmt bgr24 -s 1920x1080 -r 60 -i pipe: -pix_fmt yuv420p -c:v h264_nvenc foo.mp4
python opencv_pipe_ffmpeg_cmd.py | ffmpeg -y -f rawvideo -pix_fmt yuv420p -s 1920x1080 -r 60 -i pipe: -pix_fmt yuv420p -c:v h264_nvenc foo.mp4

# CPU h264
python opencv_pipe_ffmpeg_cmd.py | ffmpeg -y -f rawvideo -pix_fmt bgr24 -s 1920x1080 -r 60 -i pipe: -pix_fmt yuv420p foo.mp4
python opencv_pipe_ffmpeg_cmd.py | ffmpeg -y -f rawvideo -pix_fmt bgr24 -s 1920x1080 -r 60 -i pipe: foo.mp4
"""

import cv2, sys
import numpy as np

input_file = "input.mp4"
cap = cv2.VideoCapture(input_file)

if not cap.isOpened():
    print("failed to read from file!")
    exit(1)

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float `width`
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
# DONT print any other logs which will go into the pipe and affect the ffmpeg
# print(f"width x height: [{width} x {height}]")

while True:
    ret, frame = cap.read()
    if not ret:
        # DONT print any other logs which will go into the pipe to affect the ffmpeg
        # print("EOF!")
        break
    # NOTE: `frame` has `bgr24` pixel format in default in OpenCV
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)
    sys.stdout.buffer.write(frame.tobytes())
    # sys.stdout.flush()

cap.release()
