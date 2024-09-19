import aiogram
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
from config import GROUP_ID
import messages as ms
from apsched import send_balance_report

router = Router()
router.callback_query.middleware.register(CheckIsAdminMiddleware(ADMINS))


@router.callback_query(lambda callback: callback.data == "add_balance")
async def add_balance(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Начало BalanceFSM"""
    await state.set_state(BalanceFSM.pick_user)

    all_users_id, all_usernames = gs.get_all_users()

    msg = await callback.message.edit_text("Выберите пользователя для пополнения",
                                           reply_markup=kb.all_users_keyboard(all_users_id, all_usernames).as_markup())
    await state.update_data(prev_message=msg)


@router.callback_query(BalanceFSM.pick_user, lambda callback: callback.data.split("!@#$%")[0] == "add")
async def get_users_to_add(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Получение пользователя для пополнения"""
    tg_id = callback.data.split("!@#$%")[1]
    username = callback.data.split("!@#$%")[2]
    await state.update_data(tg_id=tg_id)
    await state.update_data(username=username)

    await state.set_state(BalanceFSM.amount)
    msg = await callback.message.edit_text("Укажите сумму (например: 550)",
                                           reply_markup=kb.cancel_keyboard().as_markup())

    await state.update_data(prev_message=msg)


@router.message(BalanceFSM.amount, F.text)
async def get_amount(message: types.Message, state: FSMContext, bot: aiogram.Bot) -> None:
    """Получение суммы, данных о пользователе"""
    amount = message.text
    result = amount_validate(amount)

    if result == "error":
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
        await state.update_data(type="Пополнить баланс")
        data = await state.get_data()

        data_for_record = [data["type"], data["tg_id"], data["username"], data["amount"], ""]
        gs.add_operation(data_for_record)

        await message.answer(f"Баланс пользователя <b>{data['username']}</b> успешно пополнен на <b>{data['amount']}</b> руб.✅")
        await message.answer("Выберите действие 📋", reply_markup=kb.operations_keyboard().as_markup())

        try:
            await data["prev_message"].delete()
        except TelegramBadRequest:
            pass

        # оповещение в группу
        await bot.send_message(chat_id=GROUP_ID, text=ms.create_notify_group_message(data))


@router.callback_query(lambda callback: callback.data == "get_report")
async def get_report(callback: types.CallbackQuery, bot: aiogram.Bot):
    """Получение отчета вручную"""
    balance_info = gs.get_all_info_from_balance()
    msg = "⚠️ <i>Отчет:</i>\n\n"

    if not balance_info:
        msg += "Данные отсутствуют"
        await callback.message.answer(msg)
        return

    for row in balance_info:
        msg += f"<b>{row[0]}.</b> Тг ID: {row[1]} пользователь <b>{row[4]} ({row[2]})</b> сумма: <b>{row[3]}</b> руб. \n\n"

    await callback.message.answer(msg)


@router.callback_query(lambda callback: callback.data == "cancel", StateFilter("*"))
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    """Cancel FSM and delete last message"""
    await state.clear()
    await callback.message.answer("Действие отменено ❌")
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
