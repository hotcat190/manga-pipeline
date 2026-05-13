import json
import tempfile
import os
import httpx
import asyncio
import aio_pika
from src.main import MangaPipeline

pipeline = MangaPipeline()

async def download_image(url: str, dest_path: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            f.write(response.content)

async def notify_webhook(webhook_url: str, payload: dict):
    if not webhook_url:
        return
    async with httpx.AsyncClient() as client:
        await client.post(webhook_url, json=payload)

async def process_message(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process():
        body = json.loads(message.body.decode())
        
        image_url = body.get("image_url")
        webhook_url = body.get("webhook_url")
        
        suffix = os.path.splitext(image_url)[1] or ".jpg"
        if '?' in suffix:
            suffix = suffix.split('?')[0]
            
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp_path = tmp_file.name
        tmp_file.close()

        try:
            await download_image(image_url, tmp_path)
            
            pipeline_payload = {
                "job_id": body.get("job_id"),
                "chapter_id": body.get("chapter_id"),
                "page_id": body.get("page_id"),
                "source_lang": body.get("source_lang", "ja"),
                "target_langs": body.get("target_langs", ["vi"]),
                "comic_type": body.get("comic_type", "manga"),
                "skip_translate": body.get("skip_translate", False),
                "image_path": tmp_path
            }

            result = await asyncio.to_thread(pipeline.process_job, pipeline_payload)
            
            await notify_webhook(webhook_url, result)

        except Exception as e:
            error_payload = {
                "job_id": body.get("job_id"),
                "status": "FAILED",
                "error": str(e)
            }
            await notify_webhook(webhook_url, error_payload)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

async def start_rabbitmq_consumer(rabbitmq_url: str, queue_name: str):
    connection = await aio_pika.connect_robust(rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(queue_name, durable=True)
    await queue.consume(process_message)
    return connection