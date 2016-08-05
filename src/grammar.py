import re


class Rule(object):
    DELIMITER = ' '
    DELIMITER_LEN = len(DELIMITER)

    def __init__(self, name, *rules):
        self._name = name
        self._rules = []
        for rule in rules:
            if str(rule) == rule:
                self._rules.append(RegexRule(rule))
            else:
                self._rules.append(rule)

    def match(self, text):
        text_to_match = text
        result = MatchResult()

        # Advance through the text, matching each iteration the next rule
        for i, subrule in enumerate(self._rules):

            # Ensure there is a delimiter between each rule
            if i > 0:
                delimiter, text_to_match = self.split_delimiter(text_to_match)
                result.error_position += self.DELIMITER_LEN
                if delimiter != self.DELIMITER:
                    result.is_matching = False
                    result.error_text = 'Expected a delimiter ("{}"). Instead found "{}"'.format(
                        self.DELIMITER, delimiter),
                    break

            # Try to match the next rule
            subrule_match = subrule.match(text_to_match)  # type: MatchResult
            result.tokens.update(subrule_match.tokens)

            if subrule_match.is_matching:
                # What is left after the current rule will be matched against the next rule
                text_to_match = subrule_match.remainder  # type: str

                # Track position in case we encounter an error
                result.error_position += len(subrule_match.matching_text)
            else:
                result.is_matching = False
                result.error_position += subrule_match.error_position
                result.error_text = subrule_match.error_text
                break

        if result.is_matching:
            result.matching_text = text[:-len(text_to_match)] if text_to_match else text
            result.remainder = text_to_match
            if self._name in result.tokens:
                raise GrammarTokenRedefiition(self._name)
            result.tokens[self._name] = result.matching_text
        else:
            result.matching_text = text[:result.error_position]
            result.remainder = text[result.error_position:]
        return result

    @staticmethod
    def split_delimiter(s):
        return s[:Rule.DELIMITER_LEN], s[Rule.DELIMITER_LEN:]


class RegexRule(object):
    def __init__(self, regex):
        self._regex = re.compile(regex)

    def match(self, text):
        m = self._regex.match(text)
        if m:
            return MatchResult(
                is_matching=True,
                matching_text=m.group(),
                remainder=text[m.end():],
            )
        else:
            return MatchResult(
                is_matching=False,
                remainder=text,
                error_text='"{}" does not match "{}"'.format(text, self._regex.pattern),
                error_position=0
            )


class OneOf:
    def __init__(self, *rules):
        pass


class Optional:
    def __init__(self, *rules):
        pass


class MatchResult(object):
    """
    Describes a result of a rule application.
    Attributes:
        - is_matching    - True if the text matches the rule
        - matching_text  - The portion of the text that matched the rule
        - remainder      - The remaining text that was not consumed by the rule
        - tokens         - A dictionary of tokens matched by the rule
        - error_text     - Error message if there was no match
        - error_position - The position in the text that caused the match failure
    """
    def __init__(self, **kwargs):
        self.is_matching = True
        self.matching_text = ''
        self.remainder = ''
        self.tokens = {}
        self.error_text = ''
        self.error_position = 0

        for key, value in kwargs.items():
            self.__dict__[key] = value


class GrammarTokenRedefiition(Exception):
    """Raised if a grammar contains multiple tokens with the same name"""
    def __init__(self, token_name):
        super().__init__(token_name)

