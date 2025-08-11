#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$HOME/.modal_volume_cli"
PYTHON_SCRIPT="${SCRIPT_DIR}/modal_uploader.py"

# Ask for volume name once and save it
if [ ! -f "$CONFIG_FILE" ]; then
    read -p "Enter Modal volume name: " VOL_NAME
    echo "VOLUME_NAME=$VOL_NAME" > "$CONFIG_FILE"
else
    source "$CONFIG_FILE"
    echo "Using stored volume: $VOLUME_NAME"
fi

# Ensure Python helper exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
cat <<'PYEOF' > "$PYTHON_SCRIPT"
import sys
import modal
import os

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
PYEOF
fi

# Main menu
echo "Choose operation: "
select opt in "list" "put" "rm" "quit"; do
    case $opt in
        "list")
            echo "Listing contents of volume $VOLUME_NAME:"
            modal volume get $VOLUME_NAME --tree
            break
            ;;
        "put")
            read -p "Enter comma-separated local paths: " LOCAL_PATHS
            read -p "Enter remote path (prefix, e.g. models/ or /): " REMOTE_PATH
            echo "Uploading to volume..."
            modal run "$PYTHON_SCRIPT" $VOLUME_NAME "$LOCAL_PATHS" "$REMOTE_PATH"
            break
            ;;
        "rm")
            read -p "Enter remote path to delete: " REMOTE_PATH
            echo "Deleting $REMOTE_PATH from volume $VOLUME_NAME"
            modal volume rm $VOLUME_NAME $REMOTE_PATH
            break
            ;;
        "quit")
            echo "Exiting"
            break
            ;;
        *) echo "Invalid option";;
    esac
done
