import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from src.utils.sequential_video_reader import SequentialVideoReader


class SequentialVideoReaderTest(unittest.TestCase):
    def test_jump_backward_repeat_and_end_bounds(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frames.avi"
            writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 25, (96, 64))
            self.assertTrue(writer.isOpened())
            for i in range(40):
                frame = np.full((64, 96, 3), (i * 5, 200 - i * 4, 20 + i * 3), np.uint8)
                cv2.putText(frame, str(i), (8, 42), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                writer.write(frame)
            writer.release()
            capture = cv2.VideoCapture(str(path))
            reference = []
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                reference.append(frame)
            capture.release()
            with SequentialVideoReader(path) as reader:
                for index in [0, 1, 1, 29, 3, 39, 0, 39]:
                    result = reader.at(index / 25)
                    np.testing.assert_array_equal(result, reference[index])
                    result[:] = 0
                    np.testing.assert_array_equal(reader.frame(index), reference[index])
                with self.assertRaises(IndexError):
                    reader.at(40 / 25)
                with self.assertRaises(ValueError):
                    reader.at(-0.01)


if __name__ == "__main__":
    unittest.main()
