import os
import time
import urllib.parse
from typing import List

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:4566")
S3_BUCKET = os.getenv("S3_BUCKET", "drive-clone-bucket")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
    config=Config(s3={"addressing_style": "path"}),
)

app = FastAPI(title="Drive Clone")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

KEY_SEP = "__"


def build_key(filename: str) -> str:
    ts = int(time.time() * 1000)
    safe_name = urllib.parse.quote(filename or "archivo", safe="")
    return f"{ts}{KEY_SEP}{safe_name}"


def parse_key(key: str):
    if KEY_SEP in key:
        ts_part, name_part = key.split(KEY_SEP, 1)
        try:
            ts = int(ts_part)
        except ValueError:
            ts = 0
        name = urllib.parse.unquote(name_part)
    else:
        ts, name = 0, key
    return ts, name

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    uploaded = []
    for f in files:
        content = await f.read()
        key = build_key(f.filename)
        try:
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=key,
                Body=content,
                ContentType=f.content_type or "application/octet-stream",
            )
        except ClientError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"No se pudo subir el archivo {exc}",
            )
        uploaded.append({"key": key, "name": f.filename})
    return {"uploaded": uploaded}


@app.get("/api/files")
def list_files():
    try:
        resp = s3.list_objects_v2(Bucket=S3_BUCKET)
    except ClientError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo listar el bucket {exc}",
        )

    items = []
    for obj in resp.get("Contents", []):
        ts, name = parse_key(obj["Key"])
        items.append(
            {
                "key": obj["Key"],
                "name": name,
                "size": obj["Size"],
                "uploaded_at": ts,
            }
        )
    items.sort(key=lambda x: x["uploaded_at"], reverse=True)
    return {"files": items}


@app.get("/api/download")
def download_file(key: str):
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    except ClientError:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    _, name = parse_key(key)
    content_type = obj.get("ContentType", "application/octet-stream")
    quoted = urllib.parse.quote(name)

    def iter_body():
        for chunk in obj["Body"].iter_chunks(chunk_size=8192):
            yield chunk

    return StreamingResponse(
        iter_body(),
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quoted}"},
    )


@app.get("/api/health")
def health():
    return {"status": "ok", "bucket": S3_BUCKET, "endpoint": S3_ENDPOINT}

frontend_dir = os.getenv("FRONTEND_DIR", "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
