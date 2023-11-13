from explore import *
from interface import Ui_MainWindow
from PyQt5 import QtWidgets

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


#connection, cursor = connect_to_db()
#print(f"Block size of database : {get_block_size(cursor)} bytes")

#print(get_query_plan(cursor, "SELECT * from nation, customer;"))

#print(get_buffer_hits(cursor, "SELECT * from nation, customer;"))


#cursor.execute(execution_plan_query)

#plan = cursor.fetchall()
#plan = plan[0][0][0]['Plan']
#print(plan)

