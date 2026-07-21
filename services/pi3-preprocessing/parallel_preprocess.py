"""
parallel_preprocess.py — Distributed Image Preprocessing
Splits frame into N strips, sends one to each Pi 3 worker simultaneously,
merges results back. Demonstrates Amdahl's Law in practice.
"""
import sys
import subprocess
import threading
import time
import requests
import numpy as np
sys.path.insert(0, '/home/pi/.local/lib/python3.11/site-packages')
import cv2

BACKEND_URL = "http://192.168.50.1:5000"


def get_active_workers():
    """Fetch active workers from backend (supports auto-scaling)"""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/workers", timeout=3)
        data = resp.json()
        return [(w['ip'], w['name'], w['user']) for w in data['workers']]
    except Exception:
        # Fallback to all workers
        return [
            ('192.168.50.91', 'pi3-1', 'pi3-1'),
            ('192.168.50.92', 'pi3-2', 'pi3-2'),
            ('192.168.50.93', 'pi3-3', 'pi3-3'),
            ('192.168.50.94', 'pi3-4', 'pi3-4'),
            ('192.168.50.95', 'pi3-5', 'pi3-5'),
            ('192.168.50.96', 'pi3-6', 'pi3-6'),
            ('192.168.50.97', 'pi3-7', 'pi3-7'),
        ]


def process_chunk(i, worker_ip, name, user, chunk, results):
    """Send one image strip to a Pi 3 worker via SSH"""
    ts = int(time.time() * 1000)
    local_in = f'/tmp/chunk_{i}_{ts}.jpg'
    local_out = f'/tmp/out_{i}_{ts}.jpg'
    remote_in = f'/tmp/in_{i}_{ts}.jpg'
    remote_out = f'/tmp/out_{i}_{ts}.jpg'

    cv2.imwrite(local_in, chunk)

    cmd = (
        f'scp {local_in} {user}@{worker_ip}:{remote_in} && '
        f'ssh {user}@{worker_ip} '
        f'"PYTHONPATH=/home/{user}/.local/lib/python3.11/site-packages '
        f'python3 ~/preprocess_worker.py {remote_in} {remote_out}" && '
        f'scp {user}@{worker_ip}:{remote_out} {local_out}'
    )

    ret = subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if ret == 0 and cv2.imread(local_out) is not None:
        results[i] = cv2.imread(local_out)
        print(f'{name} ✅ done!')
    else:
        results[i] = chunk  # Fallback to original chunk
        print(f'{name} ❌ failed — using original chunk')

    # Cleanup temp files
    for f in [local_in, local_out]:
        try:
            import os; os.remove(f)
        except Exception:
            pass


def process_parallel(input_path, output_path):
    """Main function: distribute frame to workers, merge results"""
    WORKERS = get_active_workers()
    print(f"Using {len(WORKERS)} workers: {[w[1] for w in WORKERS]}")

    frame = cv2.imread(input_path)
    if frame is None:
        print("Error: could not read input image")
        return

    h = frame.shape[0]
    chunk_h = h // len(WORKERS)
    results = [None] * len(WORKERS)
    threads = []
    start = time.time()

    # Launch all workers simultaneously
    for i, (worker_ip, name, user) in enumerate(WORKERS):
        s = i * chunk_h
        e = s + chunk_h if i < len(WORKERS) - 1 else h
        t = threading.Thread(
            target=process_chunk,
            args=(i, worker_ip, name, user, frame[s:e], results)
        )
        threads.append(t)
        t.start()

    # Wait for all workers to finish
    for t in threads:
        t.join()

    elapsed = time.time() - start
    print(f'Total preprocessing time: {elapsed:.3f}s | Workers: {len(WORKERS)}')

    # Merge chunks back
    cv2.imwrite(output_path, np.vstack(results))
    print(f'Output saved to {output_path}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 parallel_preprocess.py <input.jpg> <output.jpg>")
        sys.exit(1)
    process_parallel(sys.argv[1], sys.argv[2])
