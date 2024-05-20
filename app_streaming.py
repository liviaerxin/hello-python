"""
uvicorn app_streaming:app --reload
"""

from typing import Union, BinaryIO, Tuple
import os

from fastapi import FastAPI, Query, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse

FOLDER = os.path.dirname(os.path.realpath(__file__))

app = FastAPI()


############## Video Files #############
# http://127.0.0.1:8000/file/?filename=2023short.mp4
@app.get("/file", response_class=FileResponse)
async def read_file(filename: str = Query(title="resource file path in file system")):
    filepath = os.path.join(FOLDER, filename)
    if not os.path.exists(filepath):
        raise HTTPException(404, f"{filepath} not found!")

    print(f"video_path[{filepath}]")

    return FileResponse(filepath)


############### Video Stream #################
# Example page for streaming video
@app.get("/stream.html", response_class=HTMLResponse)
async def read_stream():
    print("stream.html")
    html_content = f"""
    <html>
        <head>
            <title>FastAPI video streaming</title>
        </head>
        <body>
            <video width="1200" controls muted="muted">
                <source src="http://127.0.0.1:8000/stream/?filename=2023short.mp4" type="video/mp4" />
            </video>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


# For streaming, the request and response should support `content range request` and `stream response`
@app.get("/stream", response_class=StreamingResponse)
async def stream(
    request: Request,
    filename: Union[str, None] = Query(default=None, title="resource file name, like `2023short.mp4`"),
):
    print(f"{request.headers}")

    filepath = os.path.join(FOLDER, filename)
    if not os.path.exists(filepath):
        raise HTTPException(404, f"{filepath} not found!")

    print(f"video_path[{filepath}]")

    return range_requests_response(request, file_path=filepath, content_type="video/mp4")


def range_requests_response(request: Request, file_path: str, content_type: str):
    """Returns StreamingResponse using Range Requests of a given file"""

    file_size = os.stat(file_path).st_size
    start = 0
    end = file_size - 1

    range_header = request.headers.get("Range")

    headers = {
        "content-type": content_type,
        "accept-ranges": "bytes",
        "content-encoding": "identity",
        "content-length": str(file_size),
        "access-control-expose-headers": (
            "content-type, accept-ranges, content-length, " "content-range, content-encoding"
        ),
    }

    status_code = status.HTTP_200_OK

    print(f"{start} = {end} {request.headers.get('Range')} {request.headers.get('host')}")

    if range_header is not None:
        start, end = get_range_header(range_header, file_size)
        size = end - start + 1
        headers["content-length"] = str(size)
        headers["content-range"] = f"bytes {start}-{end}/{file_size}"
        status_code = status.HTTP_206_PARTIAL_CONTENT

    return StreamingResponse(
        send_bytes_range_requests(file_path, start, end),
        headers=headers,
        status_code=status_code,
    )


# https://github.com/tiangolo/fastapi/issues/1240#issuecomment-1055396884
def send_bytes_range_requests(file_path: str, start: int, end: int, chunk_size: int = 10_000):
    """Send a file in chunks using Range Requests specification RFC7233

    `start` and `end` parameters are inclusive due to specification
    """
    with open(file_path, mode="rb") as f:
        f.seek(start)
        pos = f.tell()
        while pos <= end:
            read_size = min(chunk_size, end + 1 - pos)
            yield f.read(read_size)
            pos = f.tell()


def get_range_header(range_header: str, file_size: int) -> Tuple[int, int]:
    def _invalid_range():
        return HTTPException(
            status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail=f"Invalid request range (Range:{range_header!r})",
        )

    try:
        h = range_header.replace("bytes=", "").split("-")
        start = int(h[0]) if h[0] != "" else 0
        end = int(h[1]) if h[1] != "" else file_size - 1
    except ValueError:
        raise _invalid_range()

    if start > end or start < 0 or end > file_size - 1:
        raise _invalid_range()
    return start, end
