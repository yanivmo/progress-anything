import unittest
from datetime import datetime

from src.progress import \
    Progress, \
    UnitAlreadyStartedError


class TestProgress(unittest.TestCase):

    def test_start_statement(self):
        p = Progress()

        p.update('876543210 Start Unit-1, expect 10 steps. Just a test')
        p.update('876543211 Start Unit-2. Just a test')
        p.update('876543212 Start Unit-3, expect 10 steps')
        p.update('876543213 Start Unit-4')

        self.assertEqual(4, len(p.units))

        unit = p.units['Unit-1']
        self.assertEqual('Unit-1', unit.unit_id)
        self.assertEqual('Just a test', unit.title)
        self.assertEqual(10, unit.steps)
        self.assertEqual(datetime(1997, 10, 11, 7, 13, 30), unit.start_time)

        unit = p.units['Unit-2']
        self.assertEqual('Unit-2', unit.unit_id)
        self.assertEqual('Just a test', unit.title)
        self.assertEqual(100, unit.steps)
        self.assertEqual(datetime(1997, 10, 11, 7, 13, 31), unit.start_time)

        unit = p.units['Unit-3']
        self.assertEqual('Unit-3', unit.unit_id)
        self.assertEqual('Unit-3', unit.title)
        self.assertEqual(10, unit.steps)
        self.assertEqual(datetime(1997, 10, 11, 7, 13, 32), unit.start_time)

        unit = p.units['Unit-4']
        self.assertEqual('Unit-4', unit.unit_id)
        self.assertEqual('Unit-4', unit.title)
        self.assertEqual(100, unit.steps)
        self.assertEqual(datetime(1997, 10, 11, 7, 13, 33), unit.start_time)

        with self.assertRaises(UnitAlreadyStartedError):
            p.update('876543213 Start Unit-1')
