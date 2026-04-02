import sqlite3
import os

db_path = "example.db"
print("db file:", os.path.abspath(db_path))

con = sqlite3.connect(db_path)
cur = con.cursor()

cur.execute("create table if not exists t(x int);")
con.commit()

cur.execute("delete from t;")
con.commit()

cur.execute("insert into t(x) values (1);")
con.commit()

con.close()

# Открываем соединение заново и проверяем, сохранились ли данные
con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute("select count(*) from t;")
print("count =", cur.fetchone()[0])

con.close()