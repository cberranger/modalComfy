"""Placeholder backend for kontext model."""
import modal

app = modal.App("kontext-backend")
image = modal.Image.debian_slim(python_version="3.10")

@app.function(image=image, timeout=600)
def generate(prompt: str) -> dict:
    """Stub generation endpoint for kontext."""
    return {"model": "kontext", "prompt": prompt, "status": "not implemented"}
