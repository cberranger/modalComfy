## Setup
- Python 3.10
- `pip install modal`
- set `HUGGINGFACE_TOKEN`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DOWNLOADER_URL`
- run `python app.py`

Purpose / Component	Where to Set	Secret Name / Variables	Required key=value pairs
Hugging Face API access	Modal secret	huggingface-secret	HUGGINGFACE_TOKEN=<your_hugging_face_token>
Cloudflare R2 storage	Modal secret	cloudflare-storage	AWS_ACCESS_KEY_ID=<access_key>
AWS_SECRET_ACCESS_KEY=<secret_key>
Model downloader endpoint	Environment var	DOWNLOADER_URL	DOWNLOADER_URL=<https://your-model-downloader-service>
Protected Modal HTTP calls	HTTP headers	n/a	Modal-Key=<TOKEN_ID>
Modal-Secret=<TOKEN_SECRET>
