"""Object-by-object agreement between SAM and Spark.

A matching total is not enough: in a cluttered aisle SAM found 59 boxes and Spark 56, but only
37 of SAM's boxes had a Spark point inside. Here every carton has to be found by both.

  concept  SAM's masks for "cardboard box"
  points   Spark's one point per carton
  probes   SAM's masks for the object under each Spark point (point prompts)

A Spark point agrees with a SAM carton when it lies inside that carton's mask *and* the object
SAM finds under the point belongs to that carton: at least INSIDE of it lies within the carton,
and it is not much bigger (a point on a label finds the label, which is part of the carton; a
point that finds the whole pallet is not).
"""
from dataclasses import dataclass, field

from .gate import MIN_CONF
from .sam import Segment

INSIDE = 0.8
MAX_GROWTH = 1.5


def overlap(a: Segment, b: Segment) -> int:
    """Pixels inside both masks."""
    left, top = max(a.left, b.left), max(a.top, b.top)
    right, bottom = min(a.right, b.right), min(a.bottom, b.bottom)
    inter = 0
    aw, bw = a.right - a.left, b.right - b.left
    for y in range(top, bottom):
        ra, rb = (y - a.top) * aw, (y - b.top) * bw
        for x in range(left, right):
            inter += a.raster[ra + x - a.left] & b.raster[rb + x - b.left]
    return inter


def iou(a: Segment, b: Segment) -> float:
    inter = overlap(a, b)
    union = sum(a.raster) + sum(b.raster) - inter
    return inter / union if union else 0.0


def same_object(probe: Segment, carton: Segment) -> bool:
    area, carton_area = sum(probe.raster), sum(carton.raster)
    return (area > 0 and overlap(probe, carton) >= INSIDE * area
            and area <= MAX_GROWTH * carton_area)


@dataclass
class CrossCheck:
    agreed: list = field(default_factory=list)      # (concept index, point)
    sam_only: list = field(default_factory=list)    # concept indexes no Spark point confirms
    spark_only: list = field(default_factory=list)  # points on no SAM carton
    doubled: list = field(default_factory=list)     # concept indexes with 2+ Spark points

    @property
    def count(self) -> int | None:
        """The carton count both models support object by object, or None if they don't."""
        if self.sam_only or self.spark_only or self.doubled:
            return None
        return len(self.agreed)


def cross_check(concept: list[Segment], points: list[tuple[int, int]],
                probes: list[Segment]) -> CrossCheck:
    cartons = [s for s in concept if (s.conf or 0) >= MIN_CONF]
    probe = {s.obj: s for s in probes}                  # point prompts used ids 1..n
    out, hits = CrossCheck(), {}
    for i, (x, y) in enumerate(points):
        inside = [k for k, s in enumerate(cartons) if s.contains(x, y)]
        p = probe.get(str(i + 1))
        same = [k for k in inside if p is not None and same_object(p, cartons[k])]
        if same:
            hits.setdefault(same[0], []).append((x, y))
        else:
            out.spark_only.append((x, y))
    for k in range(len(cartons)):
        pts = hits.get(k, [])
        if not pts:
            out.sam_only.append(k)
        elif len(pts) > 1:
            out.doubled.append(k)
        else:
            out.agreed.append((k, pts[0]))
    return out
