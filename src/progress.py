from datetime import datetime

from .grammar import Rule, OneOf, Optional


class Progress:

    def __init__(self):
        self._units = {}

        unit_id = Rule('unit id').defined_as(r'[\w\-@#$%&.,:]{2,}\w')

        steps_count = Optional('steps count clause').defined_as(
            ', expect ', Rule('steps count').defined_as(r'\d+'), r' steps').nod

        title = Optional().defined_as(r'\. ', Rule('title').defined_as(r'.*')).nod

        start = Rule('start').defined_as(
            'Start ', unit_id, steps_count, title
        ).nod

        step = Rule('step').defined_as(
            'Step', unit_id, Optional('step').defined_as(r'\d+'), title
        )

        end = Rule('end').defined_as(
            'End', unit_id, OneOf(Rule('success').defined_as('SUCCESS'), Rule('failure').defined_as('FAILURE'))
        )

        self.progress_grammar = Rule().defined_as(
            Rule('timestamp').defined_as(r'\d+\.\d+|\d+'),
            OneOf(start, step, end)
        )

    def update(self, progress_statement):
        match = self.progress_grammar.match(progress_statement)
        if not match.is_matching:
            raise ProgressParsingError(progress_statement, match.error_position, match.error_text)
        else:
            if 'step' in match.tokens:
                pass

            elif 'start' in match.tokens:
                unit_id = match.tokens['unit id']
                if unit_id in self._units:
                    raise UnitAlreadyStartedError(unit_id, progress_statement)
                else:
                    self._units[unit_id] = Unit(
                        unit_id, match.tokens['timestamp'],
                        match.tokens['title'].strip() if 'title' in match.tokens else unit_id,
                        int(match.tokens['steps count']) if 'steps count' in match.tokens else 100)

            elif 'end' in match.tokens:
                pass

    @property
    def units(self):
        return self._units


class Unit(object):
    def __init__(self, unit_id, start_time, title, steps):
        self.unit_id = unit_id
        self.start_time = datetime.fromtimestamp(int(start_time))
        self.title = title
        self.steps = int(steps)

    def update(self):
        pass


class UnitAlreadyStartedError(Exception):
    def __init__(self, unit_id, statement):
        super().__init__('Unexpected start statement for a started unit {unit_id}:\n{statement}'.format(
                         unit_id=unit_id, statement=statement))


class ProgressParsingError(Exception):
    def __init__(self, statement, position, error):
        super().__init__('Statement parsing error at position {position}:\n{statement}\n{marker}\n{error}'.format(
            statement=statement,
            error=error,
            position=position,
            marker=' ' * (position - 1) + '\u25b2'))
