from modal import App, Volume, Image
import subprocess
import os
from typing import List, Tuple

app = App(name="bulk-file-downloader")

# Create a persistent volume
volume = Volume.persisted("my-persistent-volume")

# Base image with download tools
image = Image.debian_slim().apt_install("wget", "curl")

@app.function(
    image=image,
    volumes={"/data": volume},
    timeout=3600,
)
def download_single_file(url: str, filename: str, subfolder: str = "") -> dict:
    """Download a single file to the volume"""
    try:
        # Create subfolder if specified
        if subfolder:
            folder_path = f"/data/{subfolder}"
            os.makedirs(folder_path, exist_ok=True)
            filepath = f"{folder_path}/{filename}"
        else:
            filepath = f"/data/{filename}"
        
        # Check if file already exists
        if os.path.exists(filepath):
            print(f"File {filepath} already exists, skipping...")
            return {"status": "skipped", "url": url, "filepath": filepath}
        
        # Download the file
        result = subprocess.run(
            ["wget", "-O", filepath, url, "--progress=bar", "--timeout=300"], 
            check=True, 
            capture_output=True, 
            text=True
        )
        
        # Get file size
        file_size = os.path.getsize(filepath)
        print(f"Downloaded {filename} ({file_size} bytes) to {filepath}")
        
        return {
            "status": "success", 
            "url": url, 
            "filepath": filepath, 
            "size": file_size
        }
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to download {url}: {e}")
        return {"status": "failed", "url": url, "error": str(e)}
    except Exception as e:
        print(f"Unexpected error downloading {url}: {e}")
        return {"status": "error", "url": url, "error": str(e)}

@app.function(
    image=image,
    volumes={"/data": volume},
    timeout=7200,  # Longer timeout for batch operations
)
def download_files_sequential(file_list: List[Tuple[str, str]], subfolder: str = "") -> List[dict]:
    """Download multiple files sequentially in a single container"""
    results = []
    
    for url, filename in file_list:
        result = download_single_file.local(url, filename, subfolder)
        results.append(result)
    
    # Commit volume after all downloads
    volume.commit()
    print(f"Completed downloading {len(file_list)} files")
    return results

@app.function(
    image=image,
    volumes={"/data": volume},
    timeout=3600,
)
def download_files_parallel_worker(file_batch: List[Tuple[str, str]], subfolder: str = "") -> List[dict]:
    """Worker function for parallel downloading"""
    results = []
    
    for url, filename in file_batch:
        try:
            # Create subfolder if specified
            if subfolder:
                folder_path = f"/data/{subfolder}"
                os.makedirs(folder_path, exist_ok=True)
                filepath = f"{folder_path}/{filename}"
            else:
                filepath = f"/data/{filename}"
            
            # Check if file already exists
            if os.path.exists(filepath):
                print(f"File {filepath} already exists, skipping...")
                results.append({"status": "skipped", "url": url, "filepath": filepath})
                continue
            
            # Download the file
            result = subprocess.run(
                ["wget", "-O", filepath, url, "--progress=bar", "--timeout=300"], 
                check=True, 
                capture_output=True, 
                text=True
            )
            
            file_size = os.path.getsize(filepath)
            print(f"Downloaded {filename} ({file_size} bytes)")
            
            results.append({
                "status": "success", 
                "url": url, 
                "filepath": filepath, 
                "size": file_size
            })
            
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            results.append({"status": "failed", "url": url, "error": str(e)})
    
    # Commit volume after batch
    volume.commit()
    return results

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

@app.local_entrypoint()
def main():
    # Example file list - replace with your URLs and filenames
    files_to_download = [
        ("https://example.com/file1.zip", "file1.zip"),
        ("https://example.com/file2.pdf", "file2.pdf"),
        ("https://example.com/file3.json", "file3.json"),
        # Add more files here...
    ]
    
    # Option 1: Sequential download (simpler, but slower)
    print("Starting sequential download...")
    sequential_results = download_files_sequential.remote(files_to_download, "downloads")
    print("Sequential results:", sequential_results)
    
    # Option 2: Parallel download (faster for many files)
    print("\nStarting parallel download...")
    batch_size = 5  # Files per worker
    file_batches = chunk_list(files_to_download, batch_size)
    
    # Run parallel workers
    parallel_jobs = []
    for i, batch in enumerate(file_batches):
        job = download_files_parallel_worker.spawn(batch, f"parallel_batch_{i}")
        parallel_jobs.append(job)
    
    # Collect results
    all_results = []
    for job in parallel_jobs:
        batch_results = job.get()
        all_results.extend(batch_results)
    
    print(f"\nParallel download completed. Total files processed: {len(all_results)}")
    
    # Summary
    success_count = sum(1 for r in all_results if r["status"] == "success")
    failed_count = sum(1 for r in all_results if r["status"] == "failed")
    skipped_count = sum(1 for r in all_results if r["status"] == "skipped")
    
    print(f"Summary: {success_count} successful, {failed_count} failed, {skipped_count} skipped")

if __name__ == "__main__":
    main()