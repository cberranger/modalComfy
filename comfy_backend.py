import modal
import os
import subprocess
import time
from fastapi import FastAPI, Request, Response, HTTPException, BackgroundTasks
import httpx
import shutil
from fastapi.middleware.cors import CORSMiddleware

app = modal.App("comfyui-backend-coldstart")
volume = modal.Volume.from_name("comfyui-storage")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "wget")
    .pip_install(
        "requests",
        "fastapi",
        "uvicorn",
        "httpx",
        "websockets",
        "python-multipart",
    )
    .run_commands("git clone https://github.com/comfyanonymous/ComfyUI /root/ComfyUI")
    .run_commands("cd /root/ComfyUI && pip install -r requirements.txt")
)

# Standard model subdirectories
MODEL_SUBDIRS = ["unet", "lora", "loras", "checkpoints", "text_encoders", "vae", "diffusion_models"]

@app.function(
    image=image,
    gpu="A100-40GB",
    cpu=4,
    memory=8192,
    volumes={"/storage": volume},
    timeout=3600,
    scaledown_window=120,
    max_containers=1,
    min_containers=0,
)
@modal.asgi_app()
def comfyui_backend():
    import fastapi
    app = fastapi.FastAPI()

    # Download endpoint removed – use separate model_downloader service
    # 2. Startup: Mount storage and launch ComfyUI Python API backend process
    @app.on_event("startup")
    def launch_comfyui():
        os.makedirs("/storage/models", exist_ok=True)
        for sub in MODEL_SUBDIRS:
            sub_path = f"/storage/models/{sub}"
            try:
                os.makedirs(sub_path, exist_ok=True)
            except FileExistsError:
                # Directory may appear concurrently in another container
                pass
        os.makedirs("/storage/custom_nodes", exist_ok=True)
        os.makedirs("/storage/output", exist_ok=True)
        os.makedirs("/storage/input", exist_ok=True)
        os.chdir("/root/ComfyUI")

        # Replace UI folders with symlinks to persistent volume
        for folder in ["models", "custom_nodes", "output", "input"]:
            if os.path.exists(folder) or os.path.islink(folder):
                try:
                    if os.path.islink(folder) or os.path.isfile(folder):
                        os.unlink(folder)
                    else:
                        shutil.rmtree(folder)
                except Exception:
                    pass
            os.symlink(f"/storage/{folder}", folder)
        # Launch ComfyUI server (API only)
        # --disable-security: authenticates UI on trusted internal calls
        # --listen: restricts to localhost inside container
        # --port: must match below
        global comfyui_proc
        comfyui_proc = subprocess.Popen([
            "python", "main.py",
            "--listen", "0.0.0.0",
            "--port", "8188",
            "--enable-cors-header", "*",
        ])
        # Optionally wait for API readiness
        for _ in range(60):
            try:
                import urllib.request
                with urllib.request.urlopen("http://127.0.0.1:8188/") as r:
                    if r.status == 200:
                        return
            except Exception:
                time.sleep(1)
        raise RuntimeError("ComfyUI failed to start in 60s.")

    @app.on_event("shutdown")
    def stop_comfyui():
        global comfyui_proc
        if comfyui_proc:
            comfyui_proc.terminate()
            comfyui_proc.wait()

    # 3. Proxy all HTTP (and optionally WebSocket) calls to ComfyUI backend
    client = httpx.AsyncClient(base_url="http://127.0.0.1:8188", timeout=180)

    @app.api_route("/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS","HEAD"])
    async def proxy(path: str, request: Request):
        url = f"/{path}"
        if request.url.query:
            url += f"?{request.url.query}"

        headers = {k: v for k, v in request.headers.items() if k.lower() not in {"host"}}
        data = await request.body()
        resp = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=data if data else None,
        )
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers),
            media_type=resp.headers.get("content-type", "application/octet-stream"),
        )

    return app


# -------------------- CPU-only model downloader --------------------
@app.function(
    image=image,
    volumes={"/storage": volume},
    cpu=2,
    memory=4096,
    timeout=3600,
    scaledown_window=30,
    max_containers=1,
    min_containers=0,
)
@modal.asgi_app()
def model_downloader():
    import fastapi, os, requests, shutil, logging
    app = fastapi.FastAPI()
    # CORS so the ComfyUI frontend (different origin) can call this service
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.post("/download")
    async def download_model(request: fastapi.Request):
        body = await request.json()
        url = body.get("url")
        filename = body.get("filename")
        subdir = body.get("subdir", "text_encoders")
        if not url or not filename:
            raise fastapi.HTTPException(status_code=400, detail="url and filename are required.")
        if subdir not in MODEL_SUBDIRS:
            raise fastapi.HTTPException(status_code=400, detail=f"Invalid subdir. Must be one of {MODEL_SUBDIRS}.")
        full_dir = f"/storage/models/{subdir}"
        os.makedirs(full_dir, exist_ok=True)
        file_path = f"{full_dir}/{filename}"

        def download_and_commit():
            try:
                r = requests.get(url, stream=True, timeout=60)
                r.raise_for_status()
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                volume.commit()
            except requests.RequestException as e:
                logging.error("Failed to download %s: %s", url, e)
                raise fastapi.HTTPException(status_code=500, detail=f"Failed to download model: {e}")

        download_and_commit()
        return {"status": "downloaded", "path": file_path}

    return app

# (No code below is required; this file is ready for deployment and usage!)
