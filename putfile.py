import modal
import logging

logger = logging.getLogger(__name__)

app = modal.App()
image = modal.Image.debian_slim().pip_install("requests")
vol = modal.Volume.from_name("comfyui-storage")

@app.function(volumes={"/models": vol})
def putfile(url: str, filename: str, subdir: str = "text_encoders"):
    import os, requests

    allowed_dirs = ["unet", "lora", "text_encoders", "vae", "diffusion_models"]
    if subdir not in allowed_dirs:
        raise ValueError(f"Invalid subdir: {subdir}. Choose one of {allowed_dirs}")

    full_dir = f"/models/{subdir}"
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
        vol.commit()
