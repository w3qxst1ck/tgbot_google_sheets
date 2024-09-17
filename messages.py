
def create_notify_group_message(data: dict) -> str:
    message = "⚠️<i>Системное оповещение</i>\n\n"
    if data["type"] == "Зачисление":
        message += "🟢 "
    elif data["type"] == "Списание":
        message += "🔴 "
    elif data["type"] == "Пополнить баланс":
        message += f"💰 Администратор пополнил баланс <b>{data['username']}</b> на <b>{data['amount']}</b> руб."
        return message
    message += f"Пользователь <b>{data['username']}</b> выполнил операцию <b>{data['type']}</b> " \
               f"на сумму <b>{data['amount']}</b> руб."
    return message
