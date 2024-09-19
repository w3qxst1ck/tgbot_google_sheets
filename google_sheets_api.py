from datetime import datetime
from typing import List
import config

import gspread


class GoogleSheets:
    def __init__(self, filepath: str, table_name: str, cells_range: str):
        self.cells_range = cells_range
        self.gc = gspread.service_account(filename=filepath)
        self.wks_operations = self.gc.open(table_name).sheet1
        self.wks_balance = self.gc.open(table_name).get_worksheet(index=1)

        # первоначальное заполнение шапки таблиц
        self.wks_balance.batch_update([
            {
                "range": "A1:E1",
                "values": [["№", "ID(тг)", "Ник(тг)", "Текущий баланс", "Имя"]]
            }
        ])
        self.wks_operations.batch_update([
            {
                "range": "A1:G1",
                "values": [["№", "Вид операции", "ID(тг)", "Имя", "Сумма", "Комментарий", "Дата"]]
            }
        ])

    def get_next_operation_id(self) -> int:
        """Получение нового id для следующей строки таблицы операций"""
        all_values = self.wks_operations.get_all_values()
        return len(all_values)

    def get_next_balance_id(self) -> int:
        """Получение нового id для следующей строки таблицы баланса"""
        all_values = self.wks_balance.get_all_values()
        return len(all_values)

    def add_operation(self, data: List):
        """Добавление новой строки"""
        id = self.get_next_operation_id()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        data_with_id = [id, *data, timestamp]
        self.wks_operations.append_row(data_with_id, table_range=self.cells_range)
        self.update_balance(int(data[3]), data[1])

    def update_balance(self, amount: int, tg_id: str):
        """Изменение баланса"""
        user_row = self.get_user_row_from_table(tg_id)
        current_balance = int(self.wks_balance.acell(f"D{user_row}").value)
        self.wks_balance.update_cell(user_row, 4, current_balance + amount)

    def get_all_info_from_balance(self) -> list[list]:
        """Получение всех данных из таблицы Баланс"""
        all_values = self.wks_balance.get_all_values()[1:]
        return all_values

    def get_user_row_from_table(self, tg_id: str) -> int | None:
        """Получение пользователя из таблицы"""
        cell = self.wks_balance.find(tg_id)
        if cell:
            return cell.row
        return None

    def create_user_in_balance(self, tg_id: str, username: str):
        """Добавление пользователя в лист баланса"""
        # если пользователь уже нажимал старт или есть в таблице
        if self.get_user_row_from_table(tg_id):
            return

        table_id = self.get_next_balance_id()
        data = [table_id, tg_id, username, 0]
        self.wks_balance.append_row(data, table_range="A1:D1")

    def get_all_users(self):
        all_users_tg_id = self.wks_balance.col_values(2)[1:]
        all_users_username = self.wks_balance.col_values(3)[1:]
        return all_users_tg_id, all_users_username


gs = GoogleSheets(config.CREDS_FILE, config.TABLE_NAME, "A1:G1")



