`docker build --tag 'manga-pipeline:latest' .`

`docker run --detach 'manga-pipeline:latest'`

for installing requirements locally
```
pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir fastapi uvicorn python-multipart
```