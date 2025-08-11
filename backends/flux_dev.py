"""Placeholder backend for flux-dev model."""
import modal

app = modal.App("flux-dev-backend")
image = modal.Image.debian_slim(python_version="3.10")

@app.function(image=image, timeout=600)
def generate(prompt: str) -> dict:
    """Stub generation endpoint for flux-dev."""
    return {"model": "flux-dev", "prompt": prompt, "status": "not implemented"}
