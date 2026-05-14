create docker network "comic-network" if haven't already:
`docker network create comic-network`

build then run:
`docker compose build`
`docker compose up -d`

for installing requirements locally
```
pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir fastapi uvicorn python-multipart
```