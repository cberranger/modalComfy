#!/usr/bin/env python3
"""CLI helper for triggering the Modal ``model_downloader`` endpoint.

Usage:
    python model_downloader_client.py -u <model_url> -n <filename> -s <subdir>

Environment variables:
    DOWNLOADER_URL   Base URL of the model_downloader service, e.g.
                     https://chris-22--comfyui-backend-coldstart-model-downloader-dev.modal.run
                     (do **not** include the trailing slash).

Example:
    export DOWNLOADER_URL="https://your-model-downloader.modal.run"
    python model_downloader_client.py \
        -u "https://huggingface.co/lustlyai/Flux_Lustly.ai_Uncensored_nsfw_v1/resolve/main/flux_lustly-ai_v1.safetensors" \
        -n "flux_lustly.safetensors" \
        -s "lora"
"""
import argparse
import json
import os
import sys
from typing import Any

try:
    import requests  # type: ignore
except ImportError:  # pragma: no cover
    sys.stderr.write("[ERROR] 'requests' not installed. `pip install requests` and try again.\n")
    sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trigger model download via Modal downloader API")
    parser.add_argument("-u", "--url", required=True, help="Source URL of the model file")
    parser.add_argument("-n", "--name", required=True, help="Filename to save as in the volume")
    parser.add_argument(
        "-s",
        "--subdir",
        default="text_encoders",
        choices=["unet", "lora", "text_encoders", "vae", "diffusion_models"],
        help="Model subdirectory",
    )
    return parser.parse_args()


def post_json(endpoint: str, payload: dict[str, Any]) -> None:
    try:
        r = requests.post(endpoint, json=payload, timeout=30)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:  # pragma: no cover
        sys.stderr.write(f"[ERROR] HTTP request failed: {e}\n")
        sys.exit(1)

    try:
        data = r.json()
    except ValueError:  # pragma: no cover
        sys.stderr.write("[ERROR] Non-JSON response received:\n" + r.text + "\n")
        sys.exit(1)

    print(json.dumps(data, indent=2))


def main() -> None:
    args = parse_args()
    base_url = os.getenv("DOWNLOADER_URL")
    if not base_url:
        sys.stderr.write("[ERROR] Please export DOWNLOADER_URL env-var first. See script header.\n")
        sys.exit(1)

    endpoint = f"{base_url.rstrip('/')}/download"
    payload = {
        "url": args.url,
        "filename": args.name,
        "subdir": args.subdir,
    }
    post_json(endpoint, payload)


if __name__ == "__main__":
    main()
