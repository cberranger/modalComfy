"""Placeholder backend for wan2.2 model."""
import modal

app = modal.App("wan2.2-backend")
image = modal.Image.debian_slim(python_version="3.10")

@app.function(image=image, timeout=600)
def generate(prompt: str) -> dict:
    """Stub generation endpoint for wan2.2."""
    return {"model": "wan2.2", "prompt": prompt, "status": "not implemented"}
