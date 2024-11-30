import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class PaymentView(QWidget):
    buttonClickSignal = pyqtSignal('QString')

    def __init__(self, paymentApiUrl):
        super().__init__()
        self.title = "BANK PAYMENT"
        self.width = 1024
        self.height = 768
        self.paymentApiUrl = paymentApiUrl
        self.initUI()
        self.initSingalSlot()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(self.width, self.height)

        self.createPaymentTable()
        self.createControlButtons()

        self.layoutMain = QVBoxLayout()
        self.layoutMain.addWidget(self.tablePayment)
        self.layoutMain.addLayout(self.layoutButtons)
        self.setLayout(self.layoutMain)

    def initSingalSlot(self):
        self.btnDeleteAll.clicked.connect(self.slot_OnClickBtnDeleteAll)
        self.btnUpdate.clicked.connect(self.slot_OnClickBtnUpdate)
        self.btnExit.clicked.connect(self.slot_OnClickBtnExit)

    def createPaymentTable(self):
        self.tablePayment = QTableWidget()
        self.tablePayment.setColumnCount(4)
        self.tablePayment.setHorizontalHeaderLabels(['OwnerName',
                                                     'Amount',
                                                     'Reference',
                                                     'Time'])
        self.tablePayment.verticalHeader().hide()
        header = self.tablePayment.horizontalHeader()
        for i in range(4):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

    def createControlButtons(self):
        self.layoutButtons = QHBoxLayout()
        self.btnDeleteAll = QPushButton('DELETE ALL')
        self.btnUpdate = QPushButton('UPDATE')
        self.btnExit = QPushButton('EXIT')
        self.btnDeleteAll.setStyleSheet('background-color: darkgreen')
        self.btnUpdate.setStyleSheet('background-color: darkgreen')
        self.btnExit.setStyleSheet('background-color: darkred')
        self.layoutButtons.addWidget(self.btnDeleteAll)
        self.layoutButtons.addWidget(self.btnUpdate)
        self.layoutButtons.addWidget(self.btnExit)
        self.layoutButtons.setStretch(0, 1)
        self.layoutButtons.setStretch(1, 1)
        self.layoutButtons.setStretch(2, 1)

    def updatePaymentTable(self):
        try:
            self.tablePayment.setRowCount(0)
            reply = requests.get(self.paymentApiUrl + '/get-all-tranaction')
            for item in reply.json():
                rowPostion = self.tablePayment.rowCount()
                self.tablePayment.insertRow(rowPostion)
                self.tablePayment.setItem(rowPostion, 0,
                                          QTableWidgetItem(item['CounterpartAccount_TransactionOwnerName']))
                self.tablePayment.setItem(rowPostion, 1, QTableWidgetItem(item['Amount']))
                self.tablePayment.setItem(rowPostion, 2, QTableWidgetItem(item['Reference']))
                self.tablePayment.setItem(rowPostion, 3, QTableWidgetItem(item['TimestampSettled']))
        except:
            print('Payment Table Update Failed!')

    # BUTTON CLICL EVENT FINCTIONS
    def slot_OnClickBtnDeleteAll(self):
        try:
            reply = requests.get(self.paymentApiUrl + '/del-all-tranaction')
            self.updatePaymentTable()
        except:
            print('Payment DB Delete Failed!')

    def slot_OnClickBtnUpdate(self):
        self.updatePaymentTable()

    def slot_OnClickBtnExit(self):
        self.close()

    # EVENT HANDLER
    def showEvent(self, QShowEvent):
        self.updatePaymentTable()
