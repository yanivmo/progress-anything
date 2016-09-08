from datetime import datetime
from pprint import pprint

from .grammar import Rule, OneOf, Optional, RegexRule


class ProgressGrammar(Rule):
    INTEGER = RegexRule(r'\d+')
    DELIMITER = RegexRule(r' +')

    timestamp = Rule('timestamp').defined_as(r'\d+\.\d+|\d+')

    unit_id = Rule('unit_id').defined_as(r'[\w\-@#$%&.,:]{2,}\w')

    steps_count = Optional().defined_as(
        DELIMITER,
        Rule('steps_count').defined_as(INTEGER),
        r' steps'
    )

    expected_time = Optional().defined_as(
        DELIMITER,
        Rule('minutes').defined_as(INTEGER),
        ' minutes',
        Optional().defined_as(
            DELIMITER,
            Rule('seconds').defined_as(INTEGER),
            ' seconds'
        )
    )

    steps_and_time = Optional().defined_as(
        ', expect', steps_count, expected_time
    )

    description = Optional().defined_as(r'\. ', Rule('description').defined_as(r'.*'))

    start = Rule('start').defined_as(
        'Start',
        DELIMITER,
        unit_id,
        steps_and_time,
        description
    )

    step = Rule('step').defined_as(
        'Step',
        DELIMITER,
        unit_id,
        Optional().defined_as(
            DELIMITER,
            Rule('step_number').defined_as(INTEGER),
        ),
        description
    )

    end = Rule('end').defined_as(
        'End',
        DELIMITER,
        unit_id,
        DELIMITER,
        OneOf(
            Rule('success').defined_as('SUCCESS'),
            Rule('failure').defined_as('FAILURE')
        )
    )

    def __init__(self):
        super().__init__()

        self.defined_as(
            self.timestamp,
            ' ',
            OneOf(
                self.start,
                self.step,
                self.end
            )
        )


class Progress:

    def __init__(self):
        self._units = {}
        self.progress_grammar = ProgressGrammar()

    def update(self, progress_statement):
        match_result = self.progress_grammar.match(progress_statement)
        if not match_result.is_matching:
            raise ProgressParsingError(progress_statement, match_result.error_position, match_result.error_text)
        else:
            if 'step' in match_result.tokens:
                self._handle_step(match_result)
            elif 'start' in match_result.tokens:
                self._handle_start(match_result)
            elif 'end' in match_result.tokens:
                self._handle_end(match_result)
            else:
                raise AssertionError('The statement matched but none of the statement types is present')

    def _handle_start(self, match_result):
        unit_id = match_result.tokens['unit_id']
        overwitten = unit_id in self._units

        self._units[unit_id] = Unit(
            unit_id,
            match_result.tokens['timestamp'],
            match_result.tokens['description'].strip() if 'description' in match_result.tokens else unit_id,
            int(match_result.tokens['steps_count']) if 'steps_count' in match_result.tokens else 100)

        if overwitten:
            raise UnitAlreadyStartedError(unit_id, match_result.matching_text)

    def _handle_step(self, match_result):
        pass

    def _handle_end(self, match_result):
        pass

    @property
    def units(self):
        return self._units


class Unit(object):
    def __init__(self, unit_id, start_time, description, steps_count):
        self.unit_id = unit_id
        self.start_time = datetime.fromtimestamp(int(start_time))
        self.description = description
        self.steps_count = int(steps_count)
        self._steps = []

    def record_step(self, timestamp, title, value):
        pass


class UnitAlreadyStartedError(Exception):
    def __init__(self, unit_id, statement):
        super().__init__('Unexpected start statement for a started unit {unit_id}:\n{statement}'.format(
                         unit_id=unit_id, statement=statement))


class UnknownUnitError(Exception):
    def __init__(self, unit_id, statement):
        super().__init__('Progress statement for an unknown unit {unit_id}:\n{statement}'.format(
                         unit_id=unit_id, statement=statement))


class ProgressParsingError(Exception):
    def __init__(self, statement, position, error):
        super().__init__('Statement parsing error at position {position}:\n{statement}\n{marker}\n{error}'.format(
            statement=statement,
            error=error,
            position=position,
            marker=' ' * (position - 1) + '\u25b2'))
