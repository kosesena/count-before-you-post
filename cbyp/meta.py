"""Meta Model API client (OpenAI-compatible, https://api.meta.ai/v1)."""
import os
import atexit
import threading
from pathlib import Path

from openai import OpenAI, Timeout, DefaultHttpxClient
try:
    import httpx2 as httpx
except ImportError:  # SDK versions before the httpx2 migration
    import httpx

BASE_URL = "https://api.meta.ai/v1"
SPARK = "muse-spark-1.3"
SAM = "sam-3.1"
TIMEOUT = 180  # seconds


def _load_env() -> None:
    env = Path(__file__).resolve().parent.parent / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        key, sep, value = line.partition("=")
        if sep and key.strip() and key.strip() not in os.environ:
            os.environ[key.strip()] = value.strip()


UPLOAD_CHUNK_BYTES = 64 * 1024

class _UploadChunks(httpx.SyncByteStream):
    """Replayable chunks; HTTP content length and payload bytes stay unchanged."""
    def __init__(self, body):
        self.body = body

    def __iter__(self):
        for offset in range(0, len(self.body), UPLOAD_CHUNK_BYTES):
            yield self.body[offset:offset + UPLOAD_CHUNK_BYTES]


def _chunk_upload(request):
    # The SDK buffers JSON into one large ByteStream. Sending tens of MB in a
    # single TLS write can exhaust write timeouts on a slow uplink. This bounds
    # individual writes without extending timeouts or changing model inputs.
    if isinstance(request.stream, httpx.ByteStream):
        body = request.content
        if len(body) > UPLOAD_CHUNK_BYTES:
            request.stream = _UploadChunks(body)


_clients = {}
_client_lock = threading.Lock()

def _close_clients():
    for api in _clients.values():
        api.close()

atexit.register(_close_clients)

def client() -> OpenAI:
    _load_env()
    key = os.environ.get("META_API_KEY")
    if not key:
        raise RuntimeError("META_API_KEY is not set (see .env.example)")
    # The OpenAI SDK does not read META_API_KEY on its own, so pass it explicitly.
    # A SAM stream once hung for 11 minutes: no call may wait longer than TIMEOUT.
    with _client_lock:
        if key not in _clients:
            _clients[key] = OpenAI(base_url=BASE_URL, api_key=key,
                timeout=Timeout(TIMEOUT, connect=10.0, pool=10.0), max_retries=2,
                http_client=DefaultHttpxClient(event_hooks={'request': [_chunk_upload]}))
        return _clients[key]
