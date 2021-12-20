import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

class User:

    def __init__(self, user_name, user_full_name, password, user_role):
        self.user_name = user_name
        self.user_full_name = user_full_name
        self.password = password
        self.user_role = user_role


    @staticmethod
    def insert(user):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("INSERT INTO users(user_name, user_full_name, password, role) VALUES(%s, %s, %s, %s)", (user.user_name, user.user_full_name, user.password, user.user_role))
        user.id = conn_cursor.lastrowid
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return user
    
    @staticmethod
    def update(user):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("UPDATE users U SET user_name = %s, user_full_name=%s, password=%s, role=%s WHERE U.id=%s", (user.user_name, user.user_full_name, user.password, user.user_role, user.id))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return user

    @staticmethod
    def delete(user):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM users WHERE user_name=%s", (user.user_name,))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True

    @staticmethod
    def save_user(user):
        if hasattr(user, 'id') == True:
            return User.update(user)
        return User.insert(user)

    @staticmethod
    def create_user(user_name, user_full_name, password, user_role):
        user = User(user_name, user_full_name, User.hash_password(password), user_role)

        return User.save_user(user)

    @staticmethod
    def login_user(user_name, password):
        user = User.search_user(user_name)

        if user and user.check_password(password):
            return user
        
        return False

    @staticmethod
    def search_user(user_name):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM users U WHERE U.user_name = %s", (user_name,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            user = User(row[1], row[2], row[3], row[4])
            user.id = row[0]

            conn_cursor.close()
            conn_bd.close()
            return user
        else:
            pass
            #print("Error al consultar en la BD")

        conn_cursor.close()
        conn_bd.close()
        
        return False

    @staticmethod
    def search_users(user_name):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM users U WHERE U.user_name = %s", (user_name,))
        conn_bd.commit()

        list_users = []

        if conn_cursor.rowcount < 1:
            #print("Error al consultar en la BD")
            conn_cursor.close()
            conn_bd.close()
            return False
        else:
            results = conn_cursor.fetchall()
            for row in results:
                user = User(row[1], row[2], row[3], row[4])
                user.id = row[0]
                list_users.append(user)
        
        conn_cursor.close()
        conn_bd.close()

        return list_users

    @staticmethod
    def get_user_by_id(user_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM users U WHERE U.id = %s", (user_id,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            user = User(row[1], row[2], row[3], row[4])
            user.id = row[0]
            
            conn_cursor.close()
            conn_bd.close()
            return user
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False
    
    @staticmethod
    def get_all_users():
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM users U")
        conn_bd.commit()

        if conn_cursor.rowcount > 0:
            records = conn_cursor.fetchall()
            list_users = []
            for row in records:
                user = User(row[1], row[2], row[3], row[4])
                user.id = row[0]
                list_users.append(user)
            
            conn_cursor.close()
            conn_bd.close()
            return list_users
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return []


    @staticmethod
    def isAdmin(user_name):
        user = User.search_user(user_name)
        if user:
            if user.user_role == "Admin":
                return True

        return False

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password, method='sha256')

    def set_password(self, password):
        self.password = User.hash_password(password)
        return 
