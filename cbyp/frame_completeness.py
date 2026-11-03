"""Conservative frame-boundary evidence, independent of the camera reader's assertion."""
from PIL import Image, ImageOps
from .gate import MIN_CONF

def inspect_frame(path, segments):
    with Image.open(path) as raw:
        width, height = ImageOps.exif_transpose(raw).size
    # One percent guard band: a count can be correct while carton extent is unverified.
    margin_x, margin_y = max(1, width * .01), max(1, height * .01)
    touching = [dict(object=s.obj, bounds=[s.left, s.top, s.right, s.bottom], confidence=s.conf)
                for s in segments if (s.conf or 0) >= MIN_CONF and
                (s.left <= margin_x or s.top <= margin_y or
                 s.right >= width-margin_x or s.bottom >= height-margin_y)]
    return {'size': [width, height], 'margin_fraction': .01, 'boundary_objects': touching,
            'requires_review': bool(touching),
            'limitation': 'No boundary contact does not prove absence of occlusion or hidden cartons.'}
