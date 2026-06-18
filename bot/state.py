from aiogram.fsm.state import State, StatesGroup

class New(StatesGroup):
    parent = State()
    date = State()


class MilkState(StatesGroup):
    litres = State()
    date = State()
