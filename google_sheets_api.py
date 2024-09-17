from typing import List
import config

import gspread


class GoogleSheets:
    def __init__(self, filepath: str, table_name: str, cells_range: str):
        self.cells_range = cells_range
        self.gc = gspread.service_account(filename=filepath)
        self.wks_operations = self.gc.open(table_name).sheet1
        self.wks_balance = self.gc.open(table_name).get_worksheet(index=1)

    def get_next_operation_id(self) -> int:
        """Получение нового id для следующей строки таблицы"""
        all_values = self.wks_operations.get_all_values()
        return len(all_values)

    def add_operation(self, data: List):
        """Добавление новой строки"""
        id = self.get_next_operation_id()
        data_with_id = [id] + data
        self.wks_operations.append_row(data_with_id, table_range=self.cells_range)
        self.update_balance(int(data[3]))

    def update_balance(self, amount: int):
        """Изменение баланса"""
        try:
            current_balance = int(self.wks_balance.acell("B1").value)
        except TypeError:
            current_balance = 0
        self.wks_balance.update_cell(1, 2, current_balance + amount)

    def get_balance(self):
        """Получение баланса"""
        balance = self.wks_balance.acell("B1").value
        return balance


gs = GoogleSheets(config.CREDS_FILE, config.TABLE_NAME, "A1:F1")



