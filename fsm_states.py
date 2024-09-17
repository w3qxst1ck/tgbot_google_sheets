from aiogram.fsm.state import StatesGroup, State


class OperationFSM(StatesGroup):
    amount = State()
    comment = State()


class BalanceFSM(StatesGroup):
    amount = State()
