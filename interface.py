from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QCheckBox, QScrollArea
from explore import *
from sql_metadata import Parser
from functools import partial
from visualizer import *

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(799, 280)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.title = QtWidgets.QTextBrowser(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(600, 0, 191, 31))
        self.title.setObjectName("title")
        self.show_blocks = QtWidgets.QPushButton(self.centralwidget)
        self.show_blocks.setGeometry(QtCore.QRect(640, 130, 141, 51))
        self.show_blocks.setObjectName("show_blocks")
        self.show_blocks.clicked.connect(self.fshow_blocks)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(0, 80, 591, 171))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(0, 40, 181, 31))
        self.textBrowser.setObjectName("textBrowser")
        self.show_query_plan = QtWidgets.QPushButton(self.centralwidget)
        self.show_query_plan.setGeometry(QtCore.QRect(640, 190, 141, 51))
        self.show_query_plan.setObjectName("show_query_plan")
        self.show_query_plan.clicked.connect(self.fqep)
        self.btest_connection = QtWidgets.QPushButton(self.centralwidget)
        self.btest_connection.setGeometry(QtCore.QRect(640, 70, 141, 51))
        self.btest_connection.setObjectName("Test DB Connection")
        self.btest_connection.clicked.connect(self.test_connection_db)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 799, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.title.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">QEP Visualizer Team 1</span></p></body></html>"))
        self.show_blocks.setText(_translate("MainWindow", "Show Blocks"))
        self.textBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Enter SQL Query</p></body></html>"))
        self.show_query_plan.setText(_translate("MainWindow", "Show Query Plan"))
        self.btest_connection.setText(_translate("MainWindow", "Test DB Connection"))


    # Calls "Show Blocks" Pop up
    def fshow_blocks(self):
        query = self.plainTextEdit.toPlainText() # Get input from text box
        #query = "SELECT * from nation n, customer;"
        table_names = Parser(query).tables
        #print(table_names)
        print("show blocks")
        CheckBoxWindow(table_names, query).exec_()

    # Test connection to Database
    def test_connection_db(self):
        db_connection, cursor = connect_to_db()
        #print(db_connection, cursor)
        msg = QMessageBox()
        if db_connection and cursor:
            msg.setWindowTitle("Task Complete")
            msg.setText("Able to connect to DB")
            close_db_connection(db_connection, cursor)
        else:
            msg.setWindowTitle("Task Fail")
            msg.setText("Can't connect to DB. Pls UPDATE \"db_config.json\" with correct credentials")  
        msg.exec_()
    
    # # Draw Query Execution Plan
    # def fqep(self):
    #     db_connection, cursor = connect_to_db()
    #     #print(db_connection, cursor)
    #     msg = QMessageBox()
    #     # if can connect to DB
    #     if db_connection and cursor:
    #         msg.setWindowTitle("Task Complete")
    #         msg.setText("Draw execution plan HERE")
    #         print(get_query_plan(cursor, "SELECT * from nation, customer;"))
    #         close_db_connection(db_connection, cursor)
    #     else:
    #         msg.setWindowTitle("Task Fail")
    #         msg.setText("Can't connect to DB. Pls UPDATE \"db_config.json\" with correct credentials")  
    #     msg.exec_()
    
    # Draw Query Execution Plan
    def fqep(self):
        try:
            db_connection, cursor = connect_to_db()
            #print(db_connection, cursor)
            # if can connect to DB
            if db_connection and cursor:
                plan_list = get_query_plan_visualizer(cursor, "SELECT * from nation, customer;")
                print(plan_list)
                close_db_connection(db_connection, cursor)

                # Generate the figure from the query plan
                fig = create_and_draw_graph(plan_list)

                # Add the figure to the PyQt5 canvas
                self.add_matplotlib_canvas(fig)
            else:
                msg = QMessageBox()
                msg.setWindowTitle("Task Fail")
                msg.setText("Can't connect to DB. Pls UPDATE \"db_config.json\" with correct credentials")  
                msg.exec_()
        except Exception as e:
            print(e)
    
# Pop up window when "Show Blocks" is clicked
class CheckBoxWindow(QDialog):
    # Dynamatically generate a list of checkboxes
    def __init__(self, table_names, query):
        super().__init__()
        check_boxes=[]
        self.setWindowTitle("Select tables")
        self.setGeometry(100, 100, 300, 200)

        # Create a layout for checkboxes
        layout = QVBoxLayout()

        # Add checkboxes dynamically 
        for i in range(len(table_names)):
            checkbox = QCheckBox(table_names[i])
            layout.addWidget(checkbox)
            check_boxes.append(checkbox) # Append check boxes to a list
        

        self.show = QtWidgets.QPushButton("Show")
        self.show.clicked.connect(lambda: self.get_checked_box_blocks(table_names, check_boxes, query))
        layout.addWidget(self.show)
        self.setLayout(layout)

    # Returns block numbers of selected table names
    def get_checked_box_blocks(self, table_list, check_boxes, query):
        selected_tables=[]
        # Get the name of checked boxes
        for index, checkbox in enumerate(check_boxes):
            if checkbox.isChecked():
                selected_tables.append(table_list[index])
        print(f"selected tables : {selected_tables}")
        ShowBlocks(selected_tables, query).exec_()


class ShowBlocks(QDialog):
     def __init__(self, table_names, query):
        super().__init__()
        self.setWindowTitle("Show Blocks")
        self.setGeometry(100, 100, 300, 600)
        
        # Get blocks of selected tables and query
        db_connection, cursor = connect_to_db()
        blocks = get_blocks(cursor, table_names, query)
        close_db_connection(db_connection, cursor)

        #create layout to Block numbers in a scrollable area
        label = QtWidgets.QLabel("Click to view content", self)
    
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        swidget = QtWidgets.QWidget(scroll_area)
        scroll_area.setWidget(swidget)
        
        layout = QVBoxLayout(swidget)
        for table in table_names:
            block_list = blocks[table]
            for block in block_list:
                button = QtWidgets.QPushButton(f" {table} : {block}")
                button.clicked.connect(partial(self.show_block_contents, block, table))
                layout.addWidget(button)
        
        swidget.setLayout(layout)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(label)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

     def show_block_contents(self, block, table):
         db_connection, cursor = connect_to_db()
         contents, tuple_count = get_block_content(cursor, block, table)
         close_db_connection(db_connection, cursor)
         BlockContent(table, contents, tuple_count, block).exec_()
         
        
class BlockContent(QDialog):
    def __init__(self, table_names, blk_content, tuple_count, block_num):
        super().__init__()
        self.setWindowTitle("Block Contents")
        self.setGeometry(100, 100, 1000, 300)

        label = QtWidgets.QLabel(f"Number of records in Block : {block_num} of Table : {table_names} = {tuple_count}", self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        swidget = QtWidgets.QWidget(scroll_area)
        scroll_area.setWidget(swidget)
        
        layout = QVBoxLayout(swidget)
        for content in blk_content:
            string_tuple = tuple(map(str, content))
            string_tuple = ' '.join(string_tuple)
            contents =  QtWidgets.QLabel(string_tuple)
            layout.addWidget(contents)

        swidget.setLayout(layout)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(label)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
        
        '''
        self.setWindowTitle("Show Blocks")
        self.setGeometry(100, 100, 300, 600)
        
        # Get blocks of selected tables and query
        db_connection, cursor = connect_to_db()
        blocks = get_blocks(cursor, table_names, query)
        close_db_connection(db_connection, cursor)

        #create layout to Block numbers in a scrollable area
        label = QtWidgets.QLabel("Click to view content", self)
    
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        swidget = QtWidgets.QWidget(scroll_area)
        scroll_area.setWidget(swidget)
        
        layout = QVBoxLayout(swidget)
        for table in table_names:
            block_list = blocks[table]
            for block in block_list:
                button = QtWidgets.QPushButton(f" {table} : {block}")
                button.clicked.connect(partial(self.show_block_contents, block, table))
                layout.addWidget(button)
        
        swidget.setLayout(layout)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(label)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
        '''
          
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
