from field import Field, CellType
from util import Animator, Timer


class FieldProtector:
    PROTECTED = 'protected'
    NOT_PROTECTED = 'not_protected'
    BLINKING = 'blinking'

    def __init__(self, field: Field):
        self.field = field
        self._blink_animator = Animator(delay=1, max_states=2)
        self._protected_timer = Timer(delay=15)
        self._blink_timer = Timer(delay=6)
        self._state = self.NOT_PROTECTED

    def update(self):
        if self._state == self.PROTECTED:
            if self._protected_timer.tick():
                self._state = self.BLINKING
                self._blink_timer.start()
        elif self._state == self.BLINKING:
            if self._blink_timer.tick():
                self._change_base_border_tye(CellType.BRICK)
                self._state = self.NOT_PROTECTED
            else:
                state = self._blink_animator()
                self._change_base_border_tye(CellType.BRICK if state else CellType.CONCRETE)

    @property
    def cells_around_base(self):
        return [
            (11, 25),
            (11, 24),
            (11, 23),
            (12, 23),
            (13, 23),
            (14, 23),
            (14, 24),
            (14, 25)
        ]

    def _change_base_border_tye(self, ct: CellType):
        for x, y in self.cells_around_base:
            self.field.map.set_cell_col_row(x, y, ct)

    def activate(self):
        self._state = self.PROTECTED

        self._blink_timer.stop()
        self._protected_timer.start()

        self._change_base_border_tye(CellType.CONCRETE)

        # 1. защитить базу бетоном
        # 2. запустить таймер на 20 сек
        # 3. когда таймер кончится - запустить аниматор и таймер мигания на 10 сек
        # 4. пока таймер мигания - каждую секунду меняем щит с бетона на кирпич и обратно!
        ...
