"""Frame evidence from occupied mask pixels, never confidence-based deletion of edge objects."""
from PIL import Image, ImageOps
from .gate import MIN_CONF, SURE


def occupied_bounds(segment):
    """Source coordinates of nonzero mask pixels; malformed evidence fails closed."""
    width, height = segment.right-segment.left, segment.bottom-segment.top
    if width <= 0 or height <= 0 or len(segment.raster) != width*height:
        raise ValueError('Invalid boundary mask dimensions')
    mask = Image.frombytes('L', (width, height), segment.raster)
    box = mask.getbbox()
    if box is None:
        raise ValueError('Empty boundary mask')
    left, top, right, bottom = box
    return [segment.left+left, segment.top+top, segment.left+right, segment.top+bottom]


def inspect_frame(path, segments):
    with Image.open(path) as raw:
        source_size = list(raw.size)
        orientation = raw.getexif().get(274, 1)
        width, height = ImageOps.exif_transpose(raw).size
    margin_x, margin_y = max(1, width*.01), max(1, height*.01)

    def at_edge(bounds):
        left, top, right, bottom = bounds
        return (left <= margin_x or top <= margin_y or
                right >= width-margin_x or bottom >= height-margin_y)

    touching, padding_only = [], []
    for segment in segments:
        if (segment.conf or 0) < MIN_CONF:
            continue
        bounds = [segment.left, segment.top, segment.right, segment.bottom]
        if not (0 <= bounds[0] < bounds[2] <= width and 0 <= bounds[1] < bounds[3] <= height):
            raise ValueError('Boundary mask outside source image')
        occupied = occupied_bounds(segment)
        evidence = dict(object=segment.obj, bounds=bounds, occupied_bounds=occupied,
                        confidence=segment.conf,
                        confidence_band='sure' if segment.conf >= SURE else 'doubtful')
        if at_edge(occupied):
            touching.append(evidence)
        elif at_edge(bounds):
            padding_only.append(evidence)
    return {'size': [width, height], 'source_encoded_size': source_size,
            'source_exif_orientation': orientation,
            'coordinate_space': 'EXIF-oriented source pixels; model inputs are metadata-free PNG in this same orientation',
            'margin_fraction': .01,
            'boundary_objects': touching, 'bbox_padding_only': padding_only,
            'requires_review': bool(touching),
            'policy': 'All occupied edge masks at MIN_CONF or above require review, including small/doubtful objects. Only empty bounding-box padding is excluded.',
            'limitation': 'No boundary contact does not prove absence of occlusion or hidden cartons.'}
