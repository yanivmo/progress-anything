import unittest

from src.grammar import \
    RegexRule, \
    Rule, \
    Optional, \
    OneOf


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

        m = r.match('a bdefg')
        self.assertFalse(m.is_matching)
        self.assertEqual(3, m.error_position, m.error_text)

    def test_rule_without_delimiters(self):
        r = Rule('r1', 'a', 'b', 'c').nod

        m = r.match('a b cdefg')
        self.assertFalse(m.is_matching)
        self.assertEqual(1, m.error_position, m.error_text)

        m = r.match('abcdefg')
        self.assertTrue(m.is_matching)
        self.assertEqual('abc', m.matching_text)
        self.assertEqual('defg', m.remainder)
        self.assertEqual('abc', m.tokens['r1'])

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


class TestOptionalRule(unittest.TestCase):

    def test_simplest_rule(self):
        r = Optional('r1', 'a')
        m = r.match('a')
        self.assertTrue(m.is_matching)
        self.assertEqual('a', m.matching_text)
        self.assertEqual('', m.remainder)
        self.assertEqual('a', m.tokens['r1'])

        m = r.match('b')
        self.assertTrue(m.is_matching)
        self.assertEqual('', m.matching_text)
        self.assertEqual('b', m.remainder)
        self.assertEqual(0, len(m.tokens))

    def test_compound(self):
        r = Rule('r1', 'a', Optional('r1.1', 'b'), Optional('r1.2', 'c', 'd'), 'e')
        m = r.match('a b c d e')
        self.assertTrue(m.is_matching)
        self.assertEqual('a b c d e', m.matching_text)
        self.assertEqual('', m.remainder)
        self.assertEqual('a b c d e', m.tokens['r1'])
        self.assertEqual('b', m.tokens['r1.1'])
        self.assertEqual('c d', m.tokens['r1.2'])

        m = r.match('a c d e f')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertEqual('a c d e', m.matching_text)
        self.assertEqual(' f', m.remainder)
        self.assertEqual('a c d e', m.tokens['r1'])
        self.assertFalse('r1.1' in m.tokens)
        self.assertEqual('c d', m.tokens['r1.2'])

        m = r.match('a e f')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertEqual('a e', m.matching_text)
        self.assertEqual(' f', m.remainder)
        self.assertEqual('a e', m.tokens['r1'])
        self.assertFalse('r1.1' in m.tokens)
        self.assertFalse('r1.2' in m.tokens)


class TestOneOfRule(unittest.TestCase):

    def test_simplest_rule(self):
        r = OneOf('a', 'b', 'c')

        m = r.match('a')
        self.assertTrue(m.is_matching)
        self.assertEqual('a', m.matching_text)
        self.assertEqual('', m.remainder)

        m = r.match('b')
        self.assertTrue(m.is_matching)
        self.assertEqual('b', m.matching_text)
        self.assertEqual('', m.remainder)

        m = r.match('c')
        self.assertTrue(m.is_matching)
        self.assertEqual('c', m.matching_text)
        self.assertEqual('', m.remainder)

        m = r.match('d')
        self.assertFalse(m.is_matching)
        self.assertEqual('', m.matching_text)
        self.assertEqual('d', m.remainder)
        self.assertEqual(0, len(m.tokens))

    def test_compound(self):
        r = OneOf(Rule('r1', 'a'),
                  Rule('r2', 'b', '1'),
                  Rule('r3', 'b', '2'))

        m = r.match('a')
        self.assertTrue(m.is_matching)
        self.assertEqual('a', m.matching_text)
        self.assertEqual('', m.remainder)
        self.assertEqual('a', m.tokens['r1'])
        self.assertFalse('r2' in m.tokens)
        self.assertFalse('r3' in m.tokens)

        m = r.match('b 1')
        self.assertTrue(m.is_matching)
        self.assertEqual('b 1', m.matching_text)
        self.assertEqual('', m.remainder)
        self.assertEqual('b 1', m.tokens['r2'])
        self.assertFalse('r1' in m.tokens)
        self.assertFalse('r3' in m.tokens)

        m = r.match('b 3')
        self.assertFalse(m.is_matching, m.error_text)
        self.assertEqual('b ', m.matching_text)
        self.assertEqual('3', m.remainder)
        self.assertEqual(2, m.error_position)
        self.assertFalse('r1' in m.tokens)
        self.assertFalse('r2' in m.tokens)
        self.assertFalse('r3' in m.tokens)

        m = r.match('b')
        self.assertFalse(m.is_matching, m.error_text)
        self.assertEqual('b', m.matching_text)
        self.assertEqual('', m.remainder)
        self.assertEqual(1, m.error_position)
        self.assertFalse('r1' in m.tokens)
        self.assertFalse('r2' in m.tokens)
        self.assertFalse('r3' in m.tokens)
