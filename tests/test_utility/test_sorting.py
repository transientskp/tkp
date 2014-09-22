import unittest
from collections import namedtuple
from datetime import datetime, timedelta
import random
from tkp.utility.sorting import group_per_timestep

MockOrmImage = namedtuple('MockOrmImage', ['taustart_ts', 'freq_eff', 'stokes'])

now = datetime.now()

def create_input():
    """
    returns a list of mock orm images with taustart_ts, freq_eff and stokes set.
    """
    mockimages = []
    for hours in 1, 2, 3:
        taustart_ts = now - timedelta(hours=hours)
        for freq_eff in 100, 150, 200:
            for stokes in 1, 2, 3, 4:
                mockimages.append(MockOrmImage(taustart_ts=taustart_ts,
                                               freq_eff=freq_eff ** 6,
                                               stokes=stokes))

    # when we seed the RNG with a constant the shuffle will be deterministic
    random.seed(1)
    random.shuffle(mockimages)
    return mockimages


def create_output():
    mockimages = []
    for hours in 3, 2, 1:
        taustart_ts = now - timedelta(hours=hours)
        group = []
        for freq_eff in 100, 150, 200:
            for stokes in 1, 2, 3, 4:
                group.append(MockOrmImage(taustart_ts=taustart_ts,
                                          freq_eff=freq_eff ** 6,
                                          stokes=stokes))
        mockimages.append((taustart_ts, group))
    return mockimages


class TestSorting(unittest.TestCase):
    def test_sorting(self):
        input = create_input()
        should_be = create_output()
        evaluated = group_per_timestep(input)
        self.assertEqual(should_be, evaluated)
