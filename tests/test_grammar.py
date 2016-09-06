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
        r = Rule('r1').defined_as('a')

        m = r.match('a')
        self.assertTrue(m.is_matching)
        self.assertEqual('a', m.matching_text)
        self.assertEqual('', m.remainder)
        self.assertEqual('a', m.tokens['r1'])

        m = r.match('b')
        self.assertFalse(m.is_matching)
        self.assertEqual(0, m.error_position, m.error_text)

    def test_chained_simplest_rules(self):
        r = Rule('r1').defined_as('a', 'b', 'c')

        m = r.match('abcdefg')
        self.assertTrue(m.is_matching)
        self.assertEqual('abc', m.matching_text)
        self.assertEqual('defg', m.remainder)
        self.assertEqual('abc', m.tokens['r1'])

        m = r.match('abdefg')
        self.assertFalse(m.is_matching)
        self.assertEqual(2, m.error_position, m.error_text)

    def test_nested_rules(self):
        r = Rule('r1').defined_as(
                 'a',
                 Rule('r1.1').defined_as(
                      'b',
                      Rule('r1.1.1').defined_as('c', 'd')),
                 Rule('r1.2').defined_as('e'))
        m = r.match('abcde')
        self.assertTrue(m.is_matching)
        self.assertEqual('abcde', m.matching_text)
        self.assertEqual('', m.remainder)
        self.assertEqual('abcde', m.tokens['r1'])
        self.assertEqual('bcd', m.tokens['r1.1'])
        self.assertEqual('cd', m.tokens['r1.1.1'])
        self.assertEqual('e', m.tokens['r1.2'])

        m = r.match('abcef')
        self.assertFalse(m.is_matching)
        self.assertEqual(3, m.error_position, m.error_text)


class TestOptionalRule(unittest.TestCase):

    def test_simplest_rule(self):
        r = Optional('r1').defined_as('a')
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
        r = Rule('r1').defined_as(
            'a',
            Optional('r1.1').defined_as('b'),
            Optional('r1.2').defined_as('c', 'd'),
            'e')

        m = r.match('abcde')
        self.assertTrue(m.is_matching)
        self.assertEqual('abcde', m.matching_text)
        self.assertEqual('', m.remainder)
        self.assertEqual('abcde', m.tokens['r1'])
        self.assertEqual('b', m.tokens['r1.1'])
        self.assertEqual('cd', m.tokens['r1.2'])

        m = r.match('acdef')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertEqual('acde', m.matching_text)
        self.assertEqual('f', m.remainder)
        self.assertEqual('acde', m.tokens['r1'])
        self.assertFalse('r1.1' in m.tokens)
        self.assertEqual('cd', m.tokens['r1.2'])

        m = r.match('aef')
        self.assertTrue(m.is_matching, m.error_text)
        self.assertEqual('ae', m.matching_text)
        self.assertEqual('f', m.remainder)
        self.assertEqual('ae', m.tokens['r1'])
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
        r = OneOf(Rule('r1').defined_as('a'),
                  Rule('r2').defined_as('b', '1'),
                  Rule('r3').defined_as('b', '2'))

        m = r.match('a')
        self.assertTrue(m.is_matching)
        self.assertEqual('a', m.matching_text)
        self.assertEqual('', m.remainder)
        self.assertEqual('a', m.tokens['r1'])
        self.assertFalse('r2' in m.tokens)
        self.assertFalse('r3' in m.tokens)

        m = r.match('b1')
        self.assertTrue(m.is_matching)
        self.assertEqual('b1', m.matching_text)
        self.assertEqual('', m.remainder)
        self.assertEqual('b1', m.tokens['r2'])
        self.assertFalse('r1' in m.tokens)
        self.assertFalse('r3' in m.tokens)

        m = r.match('b3')
        self.assertFalse(m.is_matching, m.error_text)
        self.assertEqual('b', m.matching_text)
        self.assertEqual('3', m.remainder)
        self.assertEqual(1, m.error_position)
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
