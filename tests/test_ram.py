import unittest
import numpy as np

from codecarbon.external.hardware import RAM


# TODO: need help: test multiprocess case


class TestRAM(unittest.TestCase):
    def test_ram_diff(self):
        ram = RAM()

        for array_size in [
            # (10, 10),  # too small to be noticed
            # (100, 100),  # too small to be noticed
            (1000, 1000),  # ref for atol
            (10, 1000, 1000),
            (20, 1000, 1000),
            (100, 1000, 1000),
            (200, 1000, 1000),
            (1000, 1000, 1000),
            (2000, 1000, 1000),
        ]:
            with self.subTest(array_size=array_size):
                ref_W = ram.total_power().W
                array = np.ones(array_size, dtype=np.int8)
                n_gb = array.nbytes / (1024 ** 3)
                new_W = ram.total_power().W
                n_gb_W = (new_W - ref_W) / ram.gb_consumption
                # print(array_size, n_gb, n_gb_W)
                self.assertTrue(np.isclose(n_gb, n_gb_W, atol=1e-4))
                del array
