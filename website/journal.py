import mysql.connector
import datetime

class Journal:

    def __init__(self, user_id, create_dt, date, text, journal_id=None):
        self.id = journal_id
        self.user_id = user_id
        self.create_dt = create_dt
        self.date = date
        self.text = text


    @staticmethod
    def insert(journal):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("INSERT INTO journal(user_id, create_dt, date, text) VALUES(%s, %s, %s, %s)", (journal.user_id, journal.create_dt, journal.date, journal.text))
        journal.id = conn_cursor.lastrowid
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return journal
    
    @staticmethod
    def update(journal):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("UPDATE journal J SET user_id = %s, SET create_dt=%s, date=%s, text=%s WHERE J.id=%s", (journal.user_id, journal.create_dt, journal.date, journal.text, journal.id))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return journal

    @staticmethod
    def delete(journal):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM journal WHERE id=%s", (journal.id,))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True

    @staticmethod
    def save_journal(journal):
        if journal.id is not None:
            return Journal.update(journal)
        return Journal.insert(journal)

    @staticmethod
    def create_journal(user_id, date, text):
        journal = Journal(user_id=user_id, create_dt=datetime.datetime.now(), date=date, text=text)

        return Journal.save_journal(journal)

    @staticmethod
    def get_journal_by_id(journal_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM journal J WHERE J.id = %s", (journal_id,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            journal = Journal(journal_id=row[0], user_id=row[1], create_dt=row[2], date=row[3], text=row[4])
            
            conn_cursor.close()
            conn_bd.close()
            return journal
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False


    @staticmethod
    def get_list_journal_by_user_id(user_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM journal J WHERE J.user_id = %s", (user_id,))
        conn_bd.commit()

        if conn_cursor.rowcount > 0:
            records = conn_cursor.fetchall()
            list_journal = []
            for row in records:
                journal = Journal(journal_id=row[0], user_id=row[1], create_dt=row[2], date=row[3], text=row[4])
                list_journal.append(journal)
            
            conn_cursor.close()
            conn_bd.close()
            return list_journal
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return []