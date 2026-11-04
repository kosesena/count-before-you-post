"""One explicit pixel coordinate space for every image-model request.
Apply EXIF orientation ourselves, strip metadata, and use lossless PNG or WebP. Original
files remain unchanged and continue to be hashed by the verification workflow.
"""
import base64
import io
from PIL import Image, ImageOps


def canonical_png(path):
    with Image.open(path) as raw:
        image = ImageOps.exif_transpose(raw).convert('RGB')
        image.info.clear()
        output = io.BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()


# Large photographic PNGs can inflate inline requests and exhaust upload timeouts.
# WebP lossless preserves every decoded RGB pixel and the same coordinate space.
LOSSLESS_WEBP_THRESHOLD = 4 * 1024 * 1024

def canonical_image(path):
    png = canonical_png(path)
    if len(png) <= LOSSLESS_WEBP_THRESHOLD:
        return 'image/png', png
    with Image.open(io.BytesIO(png)) as image:
        output = io.BytesIO()
        image.save(output, format='WEBP', lossless=True, method=1)
    webp = output.getvalue()
    if len(webp) < len(png):
        return 'image/webp', webp
    return 'image/png', png


def image_data_url(path):
    mime, data = canonical_image(path)
    return 'data:' + mime + ';base64,' + base64.b64encode(data).decode('ascii')
