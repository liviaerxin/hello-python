"""_summary_
Usage:
uvicorn app_tusd:app --reload

Description:
A file resumable upload server implemented by FastAPI comply with the `tus` resumable upload protocol

[GitHub - tus/tus-resumable-upload-protocol: Open Protocol for Resumable File Uploads](https://github.com/tus/tus-resumable-upload-protocol)

"""
from fastapi import FastAPI, Header, Request, HTTPException
from starlette.requests import ClientDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, Response
from typing import Annotated, Union, Any, Hashable
import base64
import hashlib
from uuid import uuid4
from datetime import datetime, timedelta
import json
import io
import os

app = FastAPI()

# fmt: off
html_content = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Uppy</title>
    <link href="https://releases.transloadit.com/uppy/v3.3.1/uppy.min.css" rel="stylesheet">
</head>
<body>
<div id="drag-drop-area"></div>

<script type="module">
    import {Uppy, Dashboard, Tus} from "https://releases.transloadit.com/uppy/v3.3.1/uppy.min.mjs"
    var uppy = new Uppy()
        .use(Dashboard, {
            inline: true,
            target: '#drag-drop-area'
        })
        .use(Tus, {endpoint: '/files'})

    uppy.on('complete', (result) => {
        console.log('Upload complete! We’ve uploaded these files:', result.successful)
    })
</script>
</body>
</html>
"""
# fmt: on

tus_version = "1.0.0"
tus_extension = "creation,creation-defer-length,creation-with-upload,expiration,termination"
tus_checksum_algorithm = "md5,sha1,crc32"
max_size = 128849018880
location = "http://127.0.0.1:8000/files"
files_dir = "/tmp/files"

if not os.path.exists(files_dir):
    os.mkdir(files_dir)

from pydantic import BaseModel


class FileMetadata(BaseModel):
    uuid: str
    upload_metadata: dict[Hashable, str]
    upload_length: int
    offset: int = 0
    upload_part: int = 0
    created_at: str
    defer_length: bool
    upload_chunk_size: int = 0
    expires: str | None

    @classmethod
    def from_request(
        cls,
        uuid: str,
        upload_metadata: dict[Any, str],
        upload_length: int,
        created_at: str,
        defer_length: bool,
        expires: str | None = None,
    ):
        return FileMetadata(
            uuid=uuid,
            upload_metadata=upload_metadata,
            upload_length=upload_length,
            created_at=created_at,
            defer_length=defer_length,
            expires=expires,
        )


metadata_cache = {}


@app.get("/")
async def home():
    return {"message": "Hello World"}


@app.get("/upload.html")
async def read_uppy():
    return HTMLResponse(html_content)


@app.post("/files")
async def create_upload_resource(
    request: Request,
    response: Response,
    upload_metadata: str = Header(None),
    upload_length: int = Header(None),
    upload_defer_length: int = Header(None),
    content_length: int = Header(None),
    content_type: str = Header(None),
):
    if upload_defer_length is not None and upload_defer_length != 1:
        raise HTTPException(status_code=400, detail="Invalid Upload-Defer-Length")

    if upload_length is None and upload_defer_length is None:
        raise HTTPException(status_code=400, detail="Invalid Upload-Defer-Length")

    if upload_length is not None and upload_length > 0:
        defer_length = False
    else:
        defer_length = True

    # Create a new upload and store the file and metadata in the mapping
    metadata = {}
    if upload_metadata is not None and upload_metadata != "":
        # Decode the base64-encoded string
        for kv in upload_metadata.split(","):
            key, value = kv.rsplit(" ", 1)
            decoded_value = base64.b64decode(value.strip()).decode("utf-8")
            metadata[key.strip()] = decoded_value

    uuid = str(uuid4().hex)

    meta = FileMetadata.from_request(
        uuid,
        metadata,
        upload_length,
        str(datetime.now()),
        defer_length,
        None,
    )

    _write_metadata(meta)

    # Create the empty file
    open(os.path.join(files_dir, f"{uuid}"), "a").close()

    # Creation With Upload, similar with `PATCH` request
    if content_length and content_length and upload_length and not defer_length:
        assert content_type == "application/offset+octet-stream"

        meta = await _save_request_stream(request, uuid)

        if not meta:
            response.status_code = 412
            response.headers["Tus-Resumable"] = tus_version
            return

        date_expiry = datetime.now() + timedelta(days=1)
        meta.expires = str(date_expiry.isoformat())
        _write_metadata(meta)

        response.headers["Location"] = f"{location}/{uuid}"
        response.headers["Tus-Resumable"] = tus_version
        response.headers["Upload-Offset"] = str(meta.offset)
        response.headers["Upload-Expires"] = str(meta.expires)
        response.status_code = 204

        return

    # Creation Without Upload
    else:
        response.headers["Location"] = f"{location}/{uuid}"
        response.headers["Tus-Resumable"] = tus_version

        response.status_code = 201
        return


@app.head("/files/{uuid}")
async def read_file_meta(request: Request, response: Response, uuid: str):
    meta = _read_metadata(uuid)
    if meta is None or not _file_exists(uuid):
        raise HTTPException(status_code=404)

    response.headers["Tus-Resumable"] = tus_version
    response.headers["Upload-Length"] = str(meta.upload_length)
    response.headers["Upload-Offset"] = str(meta.offset)
    response.headers["Cache-Control"] = "no-store"

    if meta.defer_length:
        response.headers["Upload-Defer-Length"] = str(1)

    # Encode metadata
    if meta.upload_metadata:
        metadata_base64 = ""
        for key, value in meta.upload_metadata.items():
            metadata_base64 += f"{key} {base64.b64encode(bytes(value, 'utf-8'))},"
        response.headers["Upload-Metadata"] = metadata_base64.strip(",")

    response.status_code = 200
    return ""


@app.patch("/files/{uuid}")
async def upload_file(request: Request, response: Response, uuid: str):
    tus_resumable = request.headers["Tus-Resumable"]
    content_length = int(request.headers["Content-Length"])
    content_type = request.headers["Content-Type"]
    upload_offset = int(request.headers["Upload-Offset"])

    assert tus_resumable == tus_version
    assert content_type == "application/offset+octet-stream"

    meta = _read_metadata(uuid)

    # PATCH request against a non-existent resource
    if not meta or not _file_exists(uuid):
        response.status_code = 404
        response.headers["Tus-Resumable"] = tus_version
        return

    if meta.defer_length:
        if request.headers["Upload-Length"]:
            response.status_code = 412
            response.headers["Tus-Resumable"] = tus_version
            return
        else:
            upload_length = int(request.headers["Upload-Length"])

        meta.upload_length = upload_length
        _write_metadata(meta)

    # The Upload-Offset header's value MUST be equal to the current offset of the resource.
    if upload_offset != meta.offset:
        response.status_code = 409
        response.headers["Tus-Resumable"] = tus_version
        return

    # Saving
    meta = await _save_request_stream(request, uuid)

    # TODO: move above to `save_request_stream`
    if not meta:
        response.status_code = 412
        response.headers["Tus-Resumable"] = tus_version
        return

    if upload_offset + content_length != meta.offset:
        print(f"disconnect with client")
        response.status_code = 460
        response.headers["Tus-Resumable"] = tus_version
        return

    date_expiry = datetime.now() + timedelta(days=1)
    meta.expires = str(date_expiry.isoformat())
    _write_metadata(meta)

    # Upload file complete
    if meta.upload_length == meta.offset:
        # TODO: callbacks should be here
        pass

    response.headers["Location"] = f"{location}/{uuid}"
    response.headers["Tus-Resumable"] = tus_version
    response.headers["Upload-Offset"] = str(meta.offset)
    response.headers["Upload-Expires"] = str(meta.expires)
    response.status_code = 204
    return ""


"""
curl -v -X OPTIONS http://127.0.0.1:8000/files
"""


@app.options("/files", status_code=204)
async def read_tus_config(request: Request, response: Response):
    response.headers["Tus-Resumable"] = tus_version
    response.headers["Tus-Checksum-Algorithm"] = tus_checksum_algorithm
    response.headers["Tus-Version"] = tus_version
    response.headers["Tus-Max-Size"] = str(max_size)
    response.headers["Tus-Extension"] = tus_extension

    return ""


@app.delete("/files/{uuid}")
async def delete_file(request: Request):
    pass


async def _save_request_stream(request: Request, uuid: str, post_request: bool = False) -> FileMetadata | None:
    meta = _read_metadata(uuid)
    if not meta or not os.path.exists(os.path.join(files_dir, uuid)):
        return None

    f = open(f"{files_dir}/{uuid}", "ab")
    try:
        async for chunk in request.stream():
            chunk_size = len(chunk)
            f.write(chunk)
            meta.offset += chunk_size
            meta.upload_chunk_size = chunk_size
            meta.upload_part += 1
    except ClientDisconnect as e:
        print(f"Client disconnected: {e}")
    finally:
        _write_metadata(meta)
        f.close()

    return meta


def _read_metadata(uuid) -> FileMetadata | None:
    return metadata_cache.get(uuid)


def _write_metadata(meta: FileMetadata):
    metadata_cache[meta.uuid] = meta


def _file_exists(uuid: str) -> bool:
    return os.path.exists(os.path.join(files_dir, uuid))


def _file_path(uuid: str) -> str:
    return os.path.join(files_dir, uuid)
