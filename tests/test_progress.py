import unittest
from datetime import datetime

from src.progress import \
    Progress, \
    ProgressGrammar, \
    UnitAlreadyStartedError


class TestProgressGrammar(unittest.TestCase):

    def test_steps_count(self):
        grammar = ProgressGrammar()

        m = grammar.steps_count.match('')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertFalse(m.remainder)

        m = grammar.steps_count.match(' 10 steps')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertFalse(m.remainder)
        self.assertEqual('10', m.tokens['steps_count'])

    def test_expected_time(self):
        expected_time = ProgressGrammar().expected_time

        m = expected_time.match('')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertFalse(m.remainder)

        m = expected_time.match(' 10 minutes')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertFalse(m.remainder, m.remainder)
        self.assertEqual('10', m.tokens['minutes'])

        m = expected_time.match(' 10 minutes 27 seconds')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertFalse(m.remainder)
        self.assertEqual('10', m.tokens['minutes'])
        self.assertEqual('27', m.tokens['seconds'])

    def test_start_steps_and_time(self):
        grammar = ProgressGrammar()

        m = grammar.steps_and_time.match(', expect 10 steps')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertFalse(m.remainder)

        m = grammar.steps_and_time.match(', expect 13 steps 2 minutes 17 seconds')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertFalse(m.remainder)
        self.assertEqual('13', m.tokens['steps_count'])
        self.assertEqual('2', m.tokens['minutes'])
        self.assertEqual('17', m.tokens['seconds'])

    def test_start(self):
        grammar = ProgressGrammar()

        m = grammar.start.match('Start Unit-1, expect 10 steps. Just a test')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertFalse(m.remainder)
        self.assertEqual('Unit-1', m.tokens['unit_id'])

    def test_step(self):
        grammar = ProgressGrammar()

        m = grammar.step.match('Step Unit-1 10. Just a test')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertFalse(m.remainder)
        self.assertEqual('Unit-1', m.tokens['unit_id'])
        self.assertEqual('10', m.tokens['step_number'])

        m = grammar.step.match('Step Unit-1 10')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertFalse(m.remainder)
        self.assertEqual('Unit-1', m.tokens['unit_id'])
        self.assertEqual('10', m.tokens['step_number'])

        m = grammar.step.match('Step Unit-1. What?')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertFalse(m.remainder)
        self.assertEqual('Unit-1', m.tokens['unit_id'])
        self.assertEqual('What?', m.tokens['description'])


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
        self.assertEqual('Just a test', unit.description)
        self.assertEqual(10, unit.steps_count)
        self.assertEqual(datetime(1997, 10, 11, 7, 13, 30), unit.start_time)

        unit = p.units['Unit-2']
        self.assertEqual('Unit-2', unit.unit_id)
        self.assertEqual('Just a test', unit.description)
        self.assertEqual(100, unit.steps_count)
        self.assertEqual(datetime(1997, 10, 11, 7, 13, 31), unit.start_time)

        unit = p.units['Unit-3']
        self.assertEqual('Unit-3', unit.unit_id)
        self.assertEqual('Unit-3', unit.description)
        self.assertEqual(10, unit.steps_count)
        self.assertEqual(datetime(1997, 10, 11, 7, 13, 32), unit.start_time)

        unit = p.units['Unit-4']
        self.assertEqual('Unit-4', unit.unit_id)
        self.assertEqual('Unit-4', unit.description)
        self.assertEqual(100, unit.steps_count)
        self.assertEqual(datetime(1997, 10, 11, 7, 13, 33), unit.start_time)

        with self.assertRaises(UnitAlreadyStartedError):
            p.update('876543213 Start Unit-1. Overwrite!')
        self.assertEqual('Overwrite!', p.units['Unit-1'].description)

    def disabled_test_steps(self):
        p = Progress()

        p.update('876543210 Start Unit-1, expect 10 steps. Just a test')
        p.update('876543210 Step Unit-1')
