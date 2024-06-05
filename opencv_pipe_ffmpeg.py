# https://stackoverflow.com/questions/12503368/making-a-video-with-opencv-and-ffmpeg-how-to-find-the-right-color-format
# https://stackoverflow.com/questions/34167691/pipe-opencv-images-to-ffmpeg-using-python
# pipe from python output to ffmpeg input
"""Usage
python opencv_pipe_ffmpeg.py
"""
# This script copies the video frame by frame

import cv2
import subprocess
import shutil

# Find `ffmpeg` tool
FFMPEG_BINARY = shutil.which("ffmpeg")
if not FFMPEG_BINARY:
    print("Please install ffmpeg!")
    exit(1)


input_file = "input.mp4"
output_file = "output.mp4"

# Open the video file
cap = cv2.VideoCapture(input_file)
if not cap.isOpened():
    print("failed to read from file!")
    exit(1)

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float `width`
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
fps = cap.get(cv2.CAP_PROP_FPS)  # float `fps`

dimension = f"{width:.0f}x{height:.0f}"
f_format = "bgr24"  # remember OpenCV uses bgr format in default
fps = f"{fps:.0f}"


# Create ffmpeg pipe VideoWriter
# fmt: off
command = [
    FFMPEG_BINARY,
    "-y",
    # "-loglevel", "warning",
    "-f", "rawvideo",
    "-pix_fmt", f_format,           # pixel format            
    "-s", dimension,                # or `-video_size`
    "-r", fps,
    "-i", "pipe:",                  # input from `pipe:` or `-` or `pipe:0` for stdin, `pipe:1` for stdout, `pipe:2` for stderr
    "-an",                          # remove audio
    "-pix_fmt",  "yuv420p",
    # "-vcodec", "libx264",           # `libx264` for CPU,
    # "-c:v", "h264_nvenc",           # `h264_videotoolbox` for MAC GPU, `h264_nvenc` for NVIDIA GPU
    "-c:v", "h264_videotoolbox",           # `h264_videotoolbox` for MAC GPU, `h264_nvenc` for NVIDIA GPU              
    output_file,
]
# fmt: on

# Use `stdout=stderr=subprocess.DEVNULL`, Dont use `stdout=stderr=subprocess.PIPE`
print(" ".join(command))
proc = subprocess.Popen(
    command,
    stdin=subprocess.PIPE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

# Output to the `ffmpeg` pipe
while True:
    ret, frame = cap.read()
    if not ret:
        break
    proc.stdin.write(frame.tobytes())

cap.release()

print("EOF!")

if proc.stdin:
    proc.stdin.close()
if proc.stderr:
    proc.stderr.close()
proc.wait()
