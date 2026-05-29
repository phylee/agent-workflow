import asyncio
import time


tasks = []


async def process_jobs(queue):
    while True:
        job = await queue.get()
        tasks.append(asyncio.create_task(handle_job(job)))
        queue.task_done()


async def handle_job(job):
    time.sleep(2)
    await send_result(job)


async def send_result(job):
    if job["fail"]:
        raise RuntimeError("upstream failed")
