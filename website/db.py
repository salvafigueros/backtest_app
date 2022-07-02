from flask import Flask, g
import mysql.connector


def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

@app.after_request
def after_request(response):
    print("Fin")
    close_db()
    return response



