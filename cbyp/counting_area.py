"""Explicit operator-selected camera area; retain original evidence and crop provenance."""
import base64
import hashlib
import mimetypes
from pathlib import Path
from PIL import Image, ImageOps


def select_area(camera, selection, directory):
    if selection is None:
        return Path(camera), None
    if not isinstance(selection, dict) or selection.get('confirmed') is not True:
        raise ValueError('Confirm that the selected area contains the complete delivery.')
    box = selection.get('box')
    if not isinstance(box, list) or len(box) != 4 or any(type(v) is not int for v in box):
        raise ValueError('Counting area must contain four integer pixel coordinates.')
    source = Path(camera)
    with Image.open(source) as raw:
        im = ImageOps.exif_transpose(raw).convert('RGB')
        left, top, right, bottom = box
        if not (0 <= left < right <= im.width and 0 <= top < bottom <= im.height):
            raise ValueError('Counting area is outside the original image.')
        if right-left < 64 or bottom-top < 64:
            raise ValueError('Counting area is too small.')
        crop = Path(directory)/'camera-selected.jpg'
        im.crop(box).save(crop, quality=95, subsampling=0)
        size = list(im.size)
    def asset(path):
        data = path.read_bytes()
        return {'sha256':hashlib.sha256(data).hexdigest(),
                'data_url':'data:'+ (mimetypes.guess_type(path.name)[0] or 'image/jpeg') +';base64,'+base64.b64encode(data).decode()}
    return crop, {'scope':'operator_selected_area', 'box':box, 'coordinate_space':'EXIF-oriented original image pixels',
                  'original_size':size, 'operator_confirmed_complete_delivery':True,
                  'limitation':'Only the selected area was analyzed. Completeness is the operator’s assertion, not independently verified. Outside-area goods are not checked.',
                  'original':asset(source), 'analyzed':asset(crop)}


def attach_area(result, area):
    if area is not None:
        result['counting_area'] = area
    return result
