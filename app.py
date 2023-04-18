import sqlite3

conn = sqlite3.connect('example.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE stocks
                 (date text, trans text, symbol text, qty real, price real)''')

cursor.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

conn.commit()

cursor.execute("SELECT * FROM stocks")
print(cursor.fetchall())

conn.close()
