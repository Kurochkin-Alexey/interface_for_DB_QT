from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.uic import loadUi
import sys
import psycopg2

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('database.ui', self)

        self.db = psycopg2.connect(
            dbname="",
            user="",
            password="",
            host="localhost"
        )
        self.db.set_client_encoding('UTF8')
        self.cursor = self.db.cursor()
        self.pushButton.clicked.connect(self.load_tables)
        self.pushButton_2.clicked.connect(self.execute_dml)
        self.pushButton_3.clicked.connect(self.clear_textEdit)

    def load_tables(self):
        self.comboBox.clear()
        self.comboBox_2.clear()
        self.cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        )
        tables = [table[0] for table in self.cursor.fetchall()]
        self.comboBox.addItems(tables)
        operations = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP"]
        self.comboBox_2.addItems(operations)
        self.comboBox.currentTextChanged.connect(self.update_column_info)
        self.comboBox.currentTextChanged.connect(self.clear_textEdit)
        self.comboBox_2.currentTextChanged.connect(self.clear_textEdit)

    def execute_dml(self):
        table_name = self.comboBox.currentText()
        operation = self.comboBox_2.currentText()
        try:
            if operation == "SELECT":
                
                condition = self.textEdit.toPlainText().strip()
                if condition:
                    query = f"SELECT * FROM {table_name} WHERE {condition}"
                else:
                    query = f"SELECT * FROM {table_name}"
                self.cursor.execute(query)
                result = self.cursor.fetchall()
                if not result:
                    QMessageBox.information(self, "Info", "Таблица пуста.")
                else:
                    row_data = [', '.join(str(value) for value in row) for row in result]
                    display_text = '\n'.join(row_data)
                    self.textEdit.setPlainText(display_text)

            elif operation == "INSERT":
                data = self.textEdit.toPlainText().strip()
                rows = data.split('\n')
                values = [row.strip().split(',') for row in rows]
                query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s'] * len(values[0]))})"
                self.cursor.executemany(query, values)
                self.db.commit()
                QMessageBox.information(self, "Success", "Данные внесены в таблицу.")
                self.textEdit.setPlainText("")
                self.cursor.execute(f"SELECT * FROM {table_name}")
                result = self.cursor.fetchall()
                row_data = [', '.join(str(value) for value in row) for row in result]
                display_text = '\n'.join(row_data)
                self.textEdit.setPlainText(display_text)

            elif operation == "UPDATE":
                data_condition = self.textEdit.toPlainText().strip().split('\n')
                if len(data_condition) == 2:
                    update_data = data_condition[0]
                    condition = data_condition[1]
                    query = f"UPDATE {table_name} SET {update_data} WHERE {condition}"
                    self.cursor.execute(query)
                    self.db.commit()
                    QMessageBox.information(self, "Success", "Данные обновлены.")
                    self.textEdit.setPlainText("")
                    self.cursor.execute(f"SELECT * FROM {table_name}")
                    result = self.cursor.fetchall()
                    row_data = [', '.join(str(value) for value in row) for row in result]
                    display_text = '\n'.join(row_data)
                    self.textEdit.setPlainText(display_text)

            elif operation == "DELETE":
                conditions = self.textEdit.toPlainText().strip().split('\n')
                for condition in conditions:
                    if condition:
                        query = f"DELETE FROM {table_name} WHERE {condition}"
                        self.cursor.execute(query)
                        self.db.commit()
                QMessageBox.information(self, "Success", "Данные удалены.")
                self.textEdit.setPlainText("")
                self.cursor.execute(f"SELECT * FROM {table_name}")
                result = self.cursor.fetchall()
                row_data = [', '.join(str(value) for value in row) for row in result]
                display_text = '\n'.join(row_data)
                self.textEdit.setPlainText(display_text)

            elif operation == "DROP":
                query = f"DROP TABLE {table_name}"
                self.cursor.execute(query)
                self.db.commit()
                self.comboBox.removeItem(self.comboBox.findText(table_name))
                QMessageBox.information(self, "Success", f"Таблица {table_name} была удалена.")

        except psycopg2.Error as error:
            QMessageBox.critical(self, "Error", f"An error occurred: {error}")

    def update_column_info(self):
        try:
            self.textEdit_2.clear()
            table_name = self.comboBox.currentText()
            query = f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}';
            """
            self.cursor.execute(query)
            columns = self.cursor.fetchall()
            column_info = [f"{column[0]} ({column[1]})" for column in columns]
            self.textEdit_2.setPlainText('\n'.join(column_info))
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Update Column Info Error", f"Failed to update column info: {e}")

    def clear_textEdit(self):
        self.textEdit.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
