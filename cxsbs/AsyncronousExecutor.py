import concurrent.futures

executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

def queue(func, *args, **kwargs):
	executor.submit(func, *args, **kwargs)