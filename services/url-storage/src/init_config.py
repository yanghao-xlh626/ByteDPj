import os
import sqlite3

def init_db(DB_PATH):
    if not os.path.exists(DB_PATH):
        con = sqlite3.connect(DB_PATH)
        print('创建并连接成功')
        cur = con.cursor()
        cur.execute("CREATE TABLE URL(ID INTEGER PRIMARY KEY NOT NULL,URL TEXT NO NULL)")
        cur.execute("INSERT INTO URL (ID, URL) VALUES (1, 'https://www.example.com')")
        cur.execute("INSERT INTO URL (ID, URL) VALUES (2, 'https://www.google.com')")
        cur.execute("INSERT INTO URL (ID, URL) VALUES (3, 'https://www.github.com')")
        cur.execute("INSERT INTO URL (ID, URL) VALUES (4, 'https://www.flask.pocoo.org')")
        cur.execute("INSERT INTO URL (ID, URL) VALUES (5, 'https://www.python.org')")
        cur.execute("INSERT INTO URL (ID, URL) VALUES (6, 'https://www.sqlite.org')")
        con.commit()
        con.close()
        print("输入成功")
