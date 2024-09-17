from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from fsm_states import BalanceFSM
import keyboards as kb

from config import ADMINS
from google_sheets_api import gs
from middlewares import CheckIsAdminMiddleware
from utils import amount_validate

router = Router()
router.message.middleware.register(CheckIsAdminMiddleware(ADMINS))


@router.message(Command("balance"))
@router.callback_query(lambda callback: callback.data == "add_balance")
async def add_balance(message: types.Message, state: FSMContext) -> None:
    """Начало BalanceFSM"""
    await state.set_state(BalanceFSM.amount)

    if type(message) == types.Message:
        msg = await message.answer("Укажите сумму (только число, без знаков или указания валют по типу р. руб."
                                     "\nНапример: 1500.", reply_markup=kb.cancel_keyboard().as_markup())
        await state.update_data(prev_message=msg)

    elif type(message) == types.CallbackQuery:
        msg = await message.message.edit_text("Укажите сумму (только число, без знаков или указания валют по типу р. руб."
                             "\nНапример: 1200.", reply_markup=kb.cancel_keyboard().as_markup())
        await state.update_data(prev_message=msg)


@router.message(BalanceFSM.amount, F.text)
async def get_amount(message: types.Message, state: FSMContext) -> None:
    """Получение суммы, данных о пользователе"""
    await state.update_data(tg_id=message.from_user.id)
    await state.update_data(username=message.from_user.username)

    amount = message.text
    result = amount_validate(amount)

    if result == "error":
        await message.delete()

        data = await state.get_data()
        try:
            await data["prev_message"].delete()
        except TelegramBadRequest:
            pass

        msg = await message.answer("Введен неверный формат числа. Необходимо ввести только число. \nНапример 1200.",
                             reply_markup=kb.cancel_keyboard().as_markup())
        await state.update_data(prev_message=msg)

    else:
        await state.update_data(amount=result)
        data = await state.get_data()

        data_for_record = ["Пополнить баланс", data["tg_id"], data["username"], data["amount"], ""]
        gs.add_operation(data_for_record)

        await message.answer("Операция успешно записана! ✅")
        await message.answer("Выберите действие 📋", reply_markup=kb.operations_keyboard().as_markup())

        await message.delete()
        try:
            await data["prev_message"].delete()
        except TelegramBadRequest:
            pass


@router.callback_query(lambda callback: callback.data == "cancel", StateFilter("*"))
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    """Cancel FSM and delete last message"""
    await state.clear()
    await callback.message.answer("Действие отменено ❌")
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
