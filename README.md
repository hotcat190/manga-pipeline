clone the repo along with the `comic_text_detector` submodule
`git clone --recursive https://github.com/hotcat190/manga-pipeline`

download models from https://drive.google.com/drive/folders/1Foj9uEuktcTSpBGA2iki6Oa4N-7nfh4C?usp=sharing
and place in `./models`

create docker network "comic-network" if haven't already:
`docker network create comic-network`

build then run:
`docker compose build`
`docker compose up -d`

for installing requirements locally
```
pip install --no-cache-dir -U torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install --no-cache-dir -U -r requirements.txt
```

set env
```
$env:DEBUG_VISUALIZE="1";
$env:FLAGS_use_mkldnn="0"
$env:PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT="0"
```

run locally
`uvicorn src.api:app --host 0.0.0.0 --port 8080`

to test pipeline by running a script, refer to `test_pipeline_local.md` and `tests/test_pipeline.py`