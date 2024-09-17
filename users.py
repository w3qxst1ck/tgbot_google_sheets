import aiogram
from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from fsm_states import OperationFSM
from utils import amount_validate
from google_sheets_api import gs

import keyboards as kb
from config import GROUP_ID
import messages as ms

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message) -> None:
    """Start message"""
    await message.answer("Выберите действие 📋", reply_markup=kb.operations_keyboard().as_markup())
    tg_id = str(message.from_user.id)

    if message.from_user.username:
        username = message.from_user.username
    else:
        username = str(message.from_user.first_name or "") + " " + str(message.from_user.last_name or "")
        username.strip()

    gs.create_user_in_balance(tg_id, username)


@router.callback_query(lambda callback: callback.data.split("_")[0] == "operation")
async def plus_operation(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Начало FSM PlusBalanceFSM"""
    await state.set_state(OperationFSM.amount)

    if callback.data.split("_")[1] == "plus":
        await state.update_data(type="Зачисление")
    else:
        await state.update_data(type="Списание")

    msg = await callback.message.edit_text("Укажите сумму (например: 550)", reply_markup=kb.cancel_keyboard().as_markup())
    await state.update_data(prev_message=msg)


@router.message(OperationFSM.amount, F.text)
async def get_amount(message: types.Message, state: FSMContext) -> None:
    """Получение суммы, данных о пользователе"""
    await state.update_data(tg_id=str(message.from_user.id))

    if message.from_user.username:
        username = message.from_user.username
    else:
        username = str(message.from_user.first_name or "") + " " + str(message.from_user.last_name or "")
        username.strip()
    await state.update_data(username=username)

    amount = message.text
    result = amount_validate(amount)

    if result == "error":
        data = await state.get_data()
        prev_mess = data["prev_message"]
        await prev_mess.delete()

        msg = await message.answer("Введен неверный формат числа. Необходимо ввести только число. \nНапример 1200.",
                             reply_markup=kb.cancel_keyboard().as_markup())
        await state.update_data(prev_message=msg)

    else:
        await state.update_data(amount=result)
        await state.set_state(OperationFSM.comment)

        data = await state.get_data()
        prev_mess = data["prev_message"]
        await prev_mess.delete()

        msg = await message.answer("Укажите комментарий к операции", reply_markup=kb.cancel_keyboard().as_markup())
        await state.update_data(prev_message=msg)


@router.message(OperationFSM.comment, F.text)
async def get_comment(message: types.Message, state: FSMContext, bot: aiogram.Bot) -> None:
    """Получение комментария к операции"""
    comment = message.text
    await state.update_data(comment=comment)

    data = await state.get_data()
    if data["type"] == "Списание":
        data["amount"] *= -1

    await state.clear()

    data_for_record = [data["type"], data["tg_id"], data["username"], data["amount"], data["comment"]]
    gs.add_operation(data_for_record)

    await message.answer(f"Операция успешно записана! ✅\n\n <i>Операция: {data['type']} на сумму {data['amount']}</i>")
    await message.answer("Выберите действие 📋", reply_markup=kb.operations_keyboard().as_markup())

    prev_mess = data["prev_message"]
    await prev_mess.delete()

    # оповещение в группу
    await bot.send_message(chat_id=GROUP_ID, text=ms.create_notify_group_message(data))


@router.callback_query(lambda callback: callback.data == "cancel", StateFilter("*"))
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    """Cancel FSM and delete last message"""
    await state.clear()
    await callback.message.answer("Действие отменено ❌")
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass