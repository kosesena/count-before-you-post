"""Offline tests for the SAM x Spark object cross-check. Run: .venv/bin/python -m unittest discover tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.crosscheck import cross_check, iou  # noqa: E402
from cbyp.sam import Segment, _source_segment  # noqa: E402


def square(obj, x, y, size=10, conf=0.91):
    return Segment(str(obj), conf, x, y, x + size, y + size, bytes([1]) * size * size)


ROW = [square(k + 1, 20 * k, 0) for k in range(3)]   # three cartons side by side
CENTRES = [(20 * k + 5, 5) for k in range(3)]


class CrossCheck(unittest.TestCase):
    def test_downsampled_mask_maps_to_source_coordinates(self):
        s = _source_segment("1", .95, (10, 20, 14, 24), 2, 2, bytes([1, 0, 0, 1]))
        self.assertEqual(len(s.raster), 16)
        self.assertTrue(s.contains(10, 20))
        self.assertTrue(s.contains(13, 23))
        self.assertFalse(s.contains(12, 20))
        self.assertFalse(s.contains(14, 24))
        self.assertEqual(iou(s, square(2, 10, 20, size=4)), .5)

    def test_invalid_mask_fails_closed(self):
        with self.assertRaises(ValueError):
            _source_segment("1", .95, (0, 0, 4, 4), 2, 2, b"\x01")
        with self.assertRaises(ValueError):
            _source_segment("1", .95, (0.5, 0, 4, 4), 2, 2, bytes(4))

    def test_iou(self):
        self.assertEqual(iou(square(1, 0, 0), square(2, 0, 0)), 1.0)
        self.assertEqual(iou(square(1, 0, 0), square(2, 50, 0)), 0.0)

    def test_all_agree(self):
        probes = [square(k + 1, 20 * k, 0) for k in range(3)]
        r = cross_check(ROW, CENTRES, probes)
        self.assertEqual(r.count, 3)

    def test_carton_spark_does_not_see(self):
        # The short delivery: SAM reads a gap as a carton, Spark puts no point there.
        r = cross_check(ROW, CENTRES[:2], ROW[:2])
        self.assertEqual((r.sam_only, r.count), ([2], None))

    def test_point_on_no_carton(self):
        r = cross_check(ROW, CENTRES + [(200, 5)], ROW + [square(4, 195, 0)])
        self.assertEqual((r.spark_only, r.count), ([(200, 5)], None))

    def test_point_whose_object_is_bigger_than_the_carton(self):
        # Spark's point is inside the carton mask, but SAM's object there is the whole pallet.
        pallet = Segment("1", 0.9, 0, 0, 60, 10, bytes([1]) * 600)
        r = cross_check(ROW[:1], CENTRES[:1], [pallet])
        self.assertEqual(r.spark_only, [CENTRES[0]])

    def test_point_on_the_label_finds_the_label(self):
        label = Segment("1", 0.9, 2, 2, 8, 6, bytes([1]) * 24)
        self.assertEqual(cross_check(ROW[:1], [(5, 4)], [label]).count, 1)

    def test_two_points_on_one_carton(self):
        r = cross_check(ROW[:1], [(3, 3), (7, 7)], [ROW[0], square(2, 0, 0)])
        self.assertEqual((r.doubled, r.count), ([0], None))

    def test_low_confidence_detections_are_ignored(self):
        r = cross_check(ROW + [square(9, 100, 0, conf=0.5)], CENTRES, ROW)
        self.assertEqual(r.count, 3)


if __name__ == "__main__":
    unittest.main()
