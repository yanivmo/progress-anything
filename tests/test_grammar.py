import unittest
from src.grammar import \
    RegexRule, \
    Rule


class TestRegexRule(unittest.TestCase):

    def test_whole_match(self):
        r = RegexRule('abcde')
        m = r.match('abcde')

        self.assertTrue(m.is_matching)
        self.assertEqual('abcde', m.matching_text)
        self.assertEqual('', m.remainder)

    def test_partial_match(self):
        r = RegexRule('abcde')
        m = r.match('abcdefgh')

        self.assertTrue(m.is_matching)
        self.assertEqual('abcde', m.matching_text)
        self.assertEqual('fgh', m.remainder)

    def test_match_not_from_start(self):
        r = RegexRule('abcde')
        m = r.match('1abcde')

        self.assertFalse(m.is_matching)
        self.assertEqual(0, m.error_position)


class TestRule(unittest.TestCase):

    def test_simplest_rule(self):
        r = Rule('r1', 'a')
        m = r.match('a')
        self.assertTrue(m.is_matching)
        self.assertEqual('a', m.matching_text)
        self.assertEqual('', m.remainder)
        self.assertEqual('a', m.tokens['r1'])

        m = r.match('b')
        self.assertFalse(m.is_matching)
        self.assertEqual(0, m.error_position, m.error_text)

    def test_chained_simplest_rules(self):
        r = Rule('r1', 'a', 'b', 'c')
        m = r.match('a b cdefg')
        self.assertTrue(m.is_matching)
        self.assertEqual('a b c', m.matching_text)
        self.assertEqual('defg', m.remainder)
        self.assertEqual('a b c', m.tokens['r1'])

        m = r.match('a b defg')
        self.assertFalse(m.is_matching)
        self.assertEqual(4, m.error_position, m.error_text)

    def test_nested_rules(self):
        r = Rule('r1',
                 'a',
                 Rule('r1.1',
                      'b',
                      Rule('r1.1.1', 'c', 'd')),
                 Rule('r1.2', 'e'))
        m = r.match('a b c d e')
        self.assertTrue(m.is_matching)
        self.assertEqual('a b c d e', m.matching_text)
        self.assertEqual('', m.remainder)
        self.assertEqual('a b c d e', m.tokens['r1'])
        self.assertEqual('b c d', m.tokens['r1.1'])
        self.assertEqual('c d', m.tokens['r1.1.1'])
        self.assertEqual('e', m.tokens['r1.2'])

        m = r.match('a b c e f')
        self.assertFalse(m.is_matching)
        self.assertEqual(6, m.error_position, m.error_text)
