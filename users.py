from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from fsm_states import OperationFSM
from utils import amount_validate
from google_sheets_api import gs

import keyboards as kb

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message) -> None:
    """Start message"""
    await message.answer("Выберите действие 📋", reply_markup=kb.operations_keyboard().as_markup())


@router.callback_query(lambda callback: callback.data.split("_")[0] == "operation")
async def plus_operation(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Начало FSM PlusBalanceFSM"""
    await state.set_state(OperationFSM.amount)

    if callback.data.split("_")[1] == "plus":
        await state.update_data(type="Зачисление")
    else:
        await state.update_data(type="Списание")

    msg = await callback.message.edit_text("Укажите сумму (только число, без знаков +- или указания валют по типу р. руб."
                                     "\nНапример: 1200.)", reply_markup=kb.cancel_keyboard().as_markup())
    await state.update_data(prev_message=msg)


@router.message(OperationFSM.amount, F.text)
async def get_amount(message: types.Message, state: FSMContext) -> None:
    """Получение суммы, данных о пользователе"""
    await state.update_data(tg_id=message.from_user.id)
    await state.update_data(username=message.from_user.username)

    amount = message.text
    result = amount_validate(amount)

    if result == "error":
        await message.delete()

        data = await state.get_data()
        prev_mess = data["prev_message"]
        await prev_mess.delete()

        msg = await message.answer("Введен неверный формат числа. Необходимо ввести только число. \nНапример 1200.",
                             reply_markup=kb.cancel_keyboard().as_markup())
        await state.update_data(prev_message=msg)

    else:
        await state.update_data(amount=result)
        await state.set_state(OperationFSM.comment)
        await message.delete()

        data = await state.get_data()
        prev_mess = data["prev_message"]
        await prev_mess.delete()

        msg = await message.answer("Укажите комментарий к операции", reply_markup=kb.cancel_keyboard().as_markup())
        await state.update_data(prev_message=msg)


@router.message(OperationFSM.comment, F.text)
async def get_comment(message: types.Message, state: FSMContext) -> None:
    """Получение комментария к операции"""
    comment = message.text
    await state.update_data(comment=comment)

    data = await state.get_data()
    if data["type"] == "Списание":
        data["amount"] *= -1

    await state.clear()

    data_for_record = [data["type"], data["tg_id"], data["username"], data["amount"], data["comment"]]
    gs.add_operation(data_for_record)

    await message.answer("Операция успешно записана! ✅")
    await message.answer("Выберите действие 📋", reply_markup=kb.operations_keyboard().as_markup())

    await message.delete()
    prev_mess = data["prev_message"]
    await prev_mess.delete()


@router.callback_query(lambda callback: callback.data == "cancel", StateFilter("*"))
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    """Cancel FSM and delete last message"""
    await state.clear()
    await callback.message.answer("Действие отменено ❌")
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass