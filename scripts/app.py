import modal
import os
import subprocess
import time
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = modal.App("comfyui-app")
volume = modal.Volume.from_name("comfyui-storage")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "wget")
    .pip_install(
        "torch", "torchvision", "torchaudio",
        extra_index_url="https://download.pytorch.org/whl/cu121"
    )
    .pip_install(
        "aiohttp",
        "aiohttp-cors",
        "fastapi",
        "uvicorn",
        "httpx",
        "requests",
        "websockets",
        "python-multipart"
    )
    .run_commands("git clone https://github.com/comfyanonymous/ComfyUI /root/ComfyUI")
    .run_commands("cd /root/ComfyUI && pip install -r requirements.txt")
)

@app.function(
    image=image,
    volumes={"/storage": volume},
    timeout=1200,   # 20 minutes, adjust as needed
)
def putfile(url: str, filename: str, subdir: str = "text_encoders"):
    """Download a file into one of the allowed model subdirectories."""
    import os, requests

    allowed_dirs = ["unet", "lora", "text_encoders", "vae", "diffusion_models"]
    if subdir not in allowed_dirs:
        raise ValueError(f"Invalid subdir: {subdir}. Choose one of {allowed_dirs}")

    full_dir = f"/storage/models/{subdir}"
    os.makedirs(full_dir, exist_ok=True)

    try:
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with open(f"{full_dir}/{filename}", "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except requests.Timeout as e:
        logger.error(f"Timeout while downloading {url}: {e}")
        raise RuntimeError(f"Download timed out for {url}") from e
    except requests.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")
        raise
    else:
        volume.commit()


@app.function(
    image=image,
    volumes={"/storage": volume},
    timeout=300,
)
def list_models(subdir: str = "text_encoders"):
    """Return the list of files in a model subdirectory."""
    import os

    allowed_dirs = ["unet", "lora", "text_encoders", "vae", "diffusion_models"]
    if subdir not in allowed_dirs:
        raise ValueError(f"Invalid subdir: {subdir}. Choose one of {allowed_dirs}")

    full_dir = f"/storage/models/{subdir}"
    os.makedirs(full_dir, exist_ok=True)
    return sorted(os.listdir(full_dir))

@app.cls(
    image=image,
    gpu="A100",
    volumes={"/storage": volume},
    timeout=86400,
    container_idle_timeout=3600,
    allow_concurrent_inputs=100,
)
class ComfyUIServer:
    def __init__(self):
        self.process = None
        self.setup_complete = False

    @modal.enter()
    def setup(self):
        os.makedirs("/storage/models", exist_ok=True)
        os.makedirs("/storage/custom_nodes", exist_ok=True)
        os.makedirs("/storage/output", exist_ok=True)
        os.makedirs("/storage/input", exist_ok=True)
        os.chdir("/root/ComfyUI")
        for folder in ["models", "custom_nodes", "output", "input"]:
            if os.path.exists(folder):
                subprocess.run(["rm", "-rf", folder], check=False)
            os.symlink(f"/storage/{folder}", folder)
        self.process = subprocess.Popen([
            "python", "main.py",
            "--disable-security",
            "--listen", "127.0.0.1",
            "--port", "8188",
            "--preview-method", "auto"
        ])
        import urllib.request
        for i in range(60):
            try:
                with urllib.request.urlopen("http://127.0.0.1:8188/") as response:
                    if response.status == 200:
                        self.setup_complete = True
                        break
            except Exception:
                time.sleep(1)
        if not self.setup_complete:
            raise Exception("ComfyUI failed to start within 60 seconds")

    @modal.exit()
    def cleanup(self):
        if self.process:
            self.process.terminate()
            self.process.wait()

    @modal.asgi_app()
    def asgi_app(self):
        from fastapi import FastAPI, Request, WebSocket, Response
        import httpx, websockets, asyncio

        web_app = FastAPI()
        client = httpx.AsyncClient(base_url="http://127.0.0.1:8188", timeout=300.0)

        @web_app.on_event("shutdown")
        async def shutdown_event():
            await client.aclose()

        @web_app.websocket("/ws")
        async def websocket_proxy(websocket: WebSocket):
            await websocket.accept()
            uri = "ws://127.0.0.1:8188/ws"
            try:
                async with websockets.connect(uri) as comfyui_ws:
                    async def forward_to_comfyui():
                        try:
                            while True:
                                data = await websocket.receive_text()
                                await comfyui_ws.send(data)
                        except websockets.exceptions.ConnectionClosed:
                            pass

                    async def forward_to_client():
                        try:
                            while True:
                                data = await comfyui_ws.recv()
                                await websocket.send_text(data)
                        except websockets.exceptions.ConnectionClosed:
                            pass

                    task_to_comfyui = asyncio.create_task(forward_to_comfyui())
                    task_to_client = asyncio.create_task(forward_to_client())
                    done, pending = await asyncio.wait(
                        {task_to_comfyui, task_to_client},
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    for task in pending:
                        task.cancel()
                    await asyncio.gather(*pending, return_exceptions=True)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                await websocket.close()

        @web_app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
        async def proxy_request(request: Request, path: str):
            url = f"/{path}"
            if request.url.query:
                url += f"?{request.url.query}"
            body = await request.body()
            response = await client.request(
                method=request.method,
                url=url,
                headers={k: v for k, v in request.headers.items() if k.lower() not in ["host", "connection", "content-length"]},
                content=body if body else None,
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type", "application/octet-stream")
            )

        return web_app

@app.local_entrypoint()
def main():
    print("🚀 Deploying ComfyUI on Modal with Web Access...")
