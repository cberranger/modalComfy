import sys
import modal
import os
from pathlib import Path

volume_name = sys.argv[1]
local_files = sys.argv[2].split(",")
remote_dir = sys.argv[3]

vol = modal.Volume.persisted(volume_name)

@app.function(volumes={"/vol": vol})
def put_files():
    for local_path in local_files:
        local_path = local_path.strip()
        fname = os.path.basename(local_path)
        remote_path = os.path.join("/vol", remote_dir, fname)
        os.makedirs(os.path.dirname(remote_path), exist_ok=True)
        with open(local_path, "rb") as src, open(remote_path, "wb") as dst:
            dst.write(src.read())
        print(f"Uploaded: {local_path} -> {remote_path}")

put_files()
