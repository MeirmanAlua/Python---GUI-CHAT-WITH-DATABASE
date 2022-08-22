import sqlite3 as sql


class Database:

    def __init__(self):
        self._connectDB = sql.connect("chat.db")
        self._cursorDB = self._connectDB.cursor()

    def addUser(self, username):
        self._cursorDB.execute(f"INSERT INTO user(username) VALUES('{username}')")
        self._connectDB.commit()

    def createEntities(self):
        self._cursorDB.execute("""drop table if exists user;""")
        self._cursorDB.execute("""drop table if exists message;""")
        self._cursorDB.execute("""create table if not exists user(userId integer primary key, username text unique);""")
        self._cursorDB.execute("""create table if not exists message(messageId integer primary key, username text, message text, FOREIGN KEY (username) REFERENCES user(username) on update cascade on delete cascade );""")
        self._connectDB.commit()

    def insertText(self, data):
        self._cursorDB.execute(
            f"INSERT INTO message(username, message) VALUES('{data[0]}', '{data[1]}')")
        self._connectDB.commit()

    def isValidUsername(self, username):
        self._cursorDB.execute(f"SELECT * FROM user WHERE username='{username}'")
        row = self._cursorDB.fetchone()

        try:
            if row[1] == username:
                return False
            return True
        except TypeError:
            return True

    def closeDatabase(self):
        self._connectDB.close()


if __name__ == '__main__':
    database = Database()
    database.createEntities()
    database.closeDatabase()
