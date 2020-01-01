from field import Field
from util import Animator, Timer


class FieldProtector:
    def __init__(self, field: Field):
        self.field = field
        self._blink_animator = Animator(delay=1, max_states=2)
        self._protected_timer = Timer(delay=20)
        self._blink_timer = Timer(delay=10)

    @property
    def protected(self):
        return self._protected_timer.active or self._blink_timer.active

    def update(self):
        self._protected_timer.tick()


    def activate(self):
        if self.protected:
            return

        # 1. защитить базу бетоном
        # 2. запустить таймер на 20 сек
        # 3. когда таймер кончится - запустить аниматор и таймер мигания на 10 сек
        # 4. пока таймер мигания - каждую секунду меняем щит с бетона на кирпич и обратно!
        ...
