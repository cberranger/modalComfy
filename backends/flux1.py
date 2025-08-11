"""Placeholder backend for flux1 model."""
import modal

app = modal.App("flux1-backend")
image = modal.Image.debian_slim(python_version="3.10")

@app.function(image=image, timeout=600)
def generate(prompt: str) -> dict:
    """Stub generation endpoint for flux1."""
    return {"model": "flux1", "prompt": prompt, "status": "not implemented"}
