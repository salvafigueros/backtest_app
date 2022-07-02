import mysql.connector

class BacktestingManualOperation():


    def __init__(self, operation_id=None, backtesting_manual_id=None, quantity=None, date=None):
        self.id = operation_id
        self.backtesting_manual_id = backtesting_manual_id
        self.quantity = quantity
        self.date = date 


    @staticmethod
    def insert(backtesting_manual_operation):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("INSERT INTO backtesting_manual_operations(backtesting_manual_id, quantity, date) VALUES(%s, %s, %s)", (backtesting_manual_operation.backtesting_manual_id,
                                                                                                                                    backtesting_manual_operation.quantity, 
                                                                                                                                    backtesting_manual_operation.date))
        backtesting_manual_operation.id = conn_cursor.lastrowid
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return backtesting_manual_operation
    
    @staticmethod
    def update(backtesting_manual_operation):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("UPDATE backtesting_manual_operations B SET backtesting_manual_id=%s, quantity = %s, date=%s WHERE B.id=%s", (backtesting_manual_operation.backtesting_manual_id,
                                                                                                                                            backtesting_manual_operation.quantity, 
                                                                                                                                            backtesting_manual_operation.date,
                                                                                                                                            backtesting_manual_operation.id))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return backtesting_manual_operation

    @staticmethod
    def delete(backtesting_manual_operation):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM backtesting_manual_operations WHERE id=%s", (backtesting_manual_operation.id,))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True

    @staticmethod
    def save_backtesting_manual_operation(backtesting_manual_operation):
        if backtesting_manual_operation.id is not None:
            return BacktestingManual.update(backtesting_manual_operation)
        return BacktestingManualOperation.insert(backtesting_manual_operation)

    @staticmethod
    def create_backtesting_manual_operation(backtesting_manual_id, quantity, date):
        backtesting_manual_operation = BacktestingManualOperation(backtesting_manual_id=backtesting_manual_id, quantity=quantity, date=date)

        return BacktestingManualOperation.save_backtesting_manual_operation(backtesting_manual_operation)

    @staticmethod
    def get_backtesting_manual_operation_by_id(backtesting_manual_operation_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM backtesting_manual_operations B WHERE B.id = %s", (backtesting_manual_operation_id,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            backtesting_manual_operation = BacktestingManualOperation(operation_id=row[0], backtesting_manual_id=row[1], quantity=row[2], date=row[3])
            
            conn_cursor.close()
            conn_bd.close()
            return backtesting_manual_operation
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False


    @staticmethod
    def get_all_operations_by_backtesting_manual_id(backtesting_manual_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM backtesting_manual_operations B WHERE B.backtesting_manual_id = %s", (backtesting_manual_id,))
        conn_bd.commit()

        if conn_cursor.rowcount > 0:
            records = conn_cursor.fetchall()
            list_backtesting_manual_operation = []
            for row in records:
                backtesting_manual_operation = BacktestingManualOperation(operation_id=row[0],
                                                                            backtesting_manual_id=row[1],
                                                                            quantity=row[2],
                                                                            date=row[3])
                                                                            
                list_backtesting_manual_operation.append(backtesting_manual_operation)
            
            conn_cursor.close()
            conn_bd.close()
            return list_backtesting_manual_operation
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return []