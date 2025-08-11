import argparse
import modal
import os

app = modal.App("modal-uploader")

parser = argparse.ArgumentParser(
    description="Upload local files to a Modal volume.",
)
parser.add_argument("volume_name", help="Name of the Modal persisted volume")
parser.add_argument(
    "local_files", help="Comma-separated list of local file paths to upload"
)
parser.add_argument(
    "remote_dir", help="Directory inside the volume to copy files into"
)
args = parser.parse_args()

volume_name = args.volume_name
local_files = args.local_files.split(",")
remote_dir = args.remote_dir

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


if __name__ == "__main__":
    put_files()
