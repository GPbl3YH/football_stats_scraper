import sqlite3
import shutil

source_db = "database.db"
empty_db = "database_empty.db"

# Копируем исходную БД
shutil.copy(source_db, empty_db)

# Подключаемся к копии
con = sqlite3.connect(empty_db)
cur = con.cursor()

# Удаляем данные из всех таблиц
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = cur.fetchall()

for (table_name,) in tables:
    cur.execute(f"DELETE FROM {table_name}")

con.commit()
con.execute("VACUUM")  # очистка места
con.close()

print(f"Создана пустая копия базы: {empty_db}")
