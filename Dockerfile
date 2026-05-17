FROM python:3.11.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -U torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -U -r requirements.txt

COPY ./comic_text_detector ./comic_text_detector
COPY ./models/comictextdetector.pt ./models/comictextdetector.pt
COPY ./models/yolov12x_panels.pt ./models/yolov12x_panels.pt

COPY ./src ./src

EXPOSE 8000

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]