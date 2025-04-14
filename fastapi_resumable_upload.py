"""
Usage:
uvicorn fastapi_resumable_upload:app --reload

Description:
Http Upload file with progress and resumable features, client and server are supposed to work in their agreed protocol.

[Resumable file upload](https://javascript.info/resume-upload)

The protocol here is very simple:
- based on http request headers by adding some custom fields, `X-File-Id`, `X-Start-Byte`, `X-File-Size`,...etc.
- `X-File-Id` is a unique identifier for the file in both client and server. Here for simplicity, let client decide it unique as follows:
    `X-File-Id` = file size + "-" + file last modified + "-" + file name

client is stateless, however server is stateful with maintaining a cache of uploaded file records.

'/status' request headers:
X-File-Id: fileId
X-File-Size: fileSize
return {bytesReceived: int, fileUri: string}

'/upload' request headers:
X-File-Id: fileId
X-Start-Byte: startByte
Content-Length: fileSize
Content-Type: application/octet-stream
return {fileUri: string, bytesReceived: int}

cached file records:
{
    file_id_1: {
        "fileId": str,
        "bytesReceived": int,
        "fileSize": int,
        "fileUri": str,
    }
    ...
}
"""
from fastapi import FastAPI, Header, Request, HTTPException
from starlette.requests import ClientDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Annotated, Union
import io
import os

app = FastAPI()

# fmt: off
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Resumable Upload</title>
</head>
<body>
    <h1>Resumable Upload</h1>
    <form id="upload" action="/upload" onsubmit="uploadFile(event)">
        <input type="file" id="myFile" />
        <button>Upload (Resumes automatically)</button>
    </form>
    <button onclick="stopUpload(event)">Stop upload</button>
    <div id="fileUri">File Uri</div>
    <div id="log">Progress indication</div>
    <script>
        function log(html) {
            document.getElementById("log").innerHTML = html;
            console.log(html);
        }
        function updateFileUri(fileUri) {
            document.getElementById("fileUri").innerHTML = "fileUri: " + fileUri;
        }
        function onProgress(loaded, total) {
            log("progress " + loaded + " / " + total);
        }

        let uploader;

        function stopUpload(event) {
            event.preventDefault();
            uploader.stop();
        }

        async function uploadFile(e) {
            e.preventDefault();
            let file = document.getElementById("myFile").files[0];
            if (!file) return;
            uploader = new Uploader({ file, onProgress });
            try {
                let uploaded = await uploader.upload();
                if (uploaded) {
                    log("success");
                } else {
                    log("stopped");
                }
            } catch (err) {
                console.error(err);
                log("error");
            }
        }
    </script>
    <script>
        class Uploader {
            constructor({ file, onProgress }) {
                this.file = file;
                this.onProgress = onProgress;
                this.updateFileUri = updateFileUri;
                // create fileId that uniquely identifies the file
                // we could also add user session identifier (if had one), to make it even more unique
                this.fileId = file.size + "-" + file.lastModified + "-" + file.name;
            }

            async getUploadedBytes() {
                let response = await fetch("/status", {
                    headers: {
                        "X-File-Id": this.fileId,
                        "X-File-Size": this.file.size,
                    },
                });
                if (response.status != 200) {
                    throw new Error("Can't get uploaded bytes: " + response.statusText);
                }
                let { bytesReceived, fileUri} = await response.json();
                return [bytesReceived, fileUri];
            }

            async upload() {
                [this.startByte, this.fileUri] = await this.getUploadedBytes();
                this.updateFileUri(this.fileUri)
                let xhr = (this.xhr = new XMLHttpRequest());
                xhr.open("POST", "/upload", true);
                xhr.setRequestHeader("X-File-Id", this.fileId);
                xhr.setRequestHeader("X-Start-Byte", this.startByte);
                // Let xhr calculate this
                // xhr.setRequestHeader("Content-Length", this.file.slice(this.startByte).size);
                xhr.setRequestHeader("Content-Type", "application/octet-stream");
                xhr.upload.onprogress = (e) => {
                    this.onProgress(this.startByte + e.loaded, this.startByte + e.total);
                };
                console.log("send the file, starting from", this.startByte);
                xhr.send(this.file.slice(this.startByte));
                return await new Promise((resolve, reject) => {
                    xhr.onload = xhr.onerror = () => {
                        console.log(
                            "upload end status:" + xhr.status + " text:" + xhr.statusText
                        );
                        if (xhr.status == 200) {
                            let res = JSON.parse(xhr.responseText);
                            log(res)
                            this.updateFileUri(res.fileUri)
                            resolve(true);
                        } else {
                            reject(new Error("Upload failed: " + xhr.statusText));
                        }
                    };
                    xhr.onabort = () => resolve(false);
                });
            }

            stop() {
                if (this.xhr) {
                    this.xhr.abort();
                }
            }
        }
    </script>
</body>
</html>
"""
# fmt: on

Uploads_Cache = {}


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


app = FastAPI()


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


@app.get("/")
async def home(request: Request):
    async for chunk in request.stream():
        # The last chunk is b""
        chunk_size = len(chunk)
        print(f"chunk_size: {chunk_size}")

    return {"message": "Hello World"}


@app.get("/upload.html")
async def read_upload():
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/status")
async def read_status(request: Request):
    fileId = request.headers["X-File-Id"]
    fileSize = int(request.headers["X-File-Size"])

    uploadFile = Uploads_Cache.get(fileId)

    if uploadFile:
        assert (
            os.path.getsize(uploadFile["fileUri"]) == uploadFile["bytesReceived"]
        ), "actual file bytes must match record bytes!"
        return {
            "bytesReceived": uploadFile["bytesReceived"],
            "fileUri": uploadFile["fileUri"],
        }
    else:
        return {"bytesReceived": 0, "fileUri": ""}


@app.post("/upload")
async def upload(request: Request):
    fileId = request.headers["X-File-Id"]
    startByte = int(request.headers["X-Start-Byte"])
    uploadfileSize = int(request.headers["Content-Length"])
    fileSize = uploadfileSize + startByte

    # Create a new file
    if not Uploads_Cache.get(fileId):
        # fileUri = "/dev/null"
        # could use a real path instead, e.g.
        fileUri = os.path.join("/tmp", fileId + ".uploading")

        uploadFile = Uploads_Cache[fileId] = {
            "fileId": fileId,
            "bytesReceived": 0,
            "fileSize": fileSize,
            "fileUri": fileUri,
        }

        assert startByte == 0, "startByte must be 0"

        fs = io.FileIO(fileUri, "w")
        print(f"File create: {fileUri}")
    # Check the size and append to existing one
    else:
        uploadFile = Uploads_Cache[fileId]
        fileUri = uploadFile["fileUri"]

        assert uploadFile["bytesReceived"] == startByte, "startByte must match record bytes!"

        fs = io.FileIO(fileUri, "a")
        print(f"File reopened: {fileUri}")

    try:
        async for chunk in request.stream():
            # The last chunk is b""
            chunk_size = len(chunk)
            print(f"chunk_size: {chunk_size}")
            fs.write(chunk)
            uploadFile["bytesReceived"] += chunk_size

        # Remove the file record
        del Uploads_Cache[fileId]
        fs.seek(0, os.SEEK_END)
        actualSize = fs.tell()
        fs.close()

        assert fileSize == actualSize, "actual file size must match record size!"

        # Rename the file
        uploadFile["fileUri"] = os.path.splitext(fileUri)[0]
        print(f"renamed file: {fileUri} to {uploadFile['fileUri']}")
        os.rename(fileUri, uploadFile["fileUri"])

        return {
            "bytesReceived": uploadFile["bytesReceived"],
            "fileUri": uploadFile["fileUri"],
        }
    except ClientDisconnect as e:
        print(f"exception: {e}")

        raise HTTPException(
            status_code=500,
            detail={
                "message": "File unfinished, stopped at",
                "startByte": startByte,
                "bytesReceived": uploadFile["bytesReceived"],
            },
        )
