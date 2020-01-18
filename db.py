import sqlite3

conn = sqlite3.connect("data.db")
c = conn.cursor()

def create():
    c.execute("""CREATE TABLE questions (
        id integer PRIMARY KEY AUTOINCREMENT,
        title text
    )
    """)
    conn.commit()
    c.execute("""CREATE TABLE options (
        sno integer PRIMARY KEY AUTOINCREMENT,
        qid integer, 
        title text
    )
    """)
    conn.commit()
    
def addquestion(text):
    c.execute("INSERT INTO questions (title) VALUES(?)", (text,))
    conn.commit()

def addoptions(id, text):
    c.execute("INSERT INTO options (qid, title) VALUES(?, ?)", (id, text))
    conn.commit()

create()
conn.commit()