from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class MainWnd(QWidget):
    buttonClickSignal = pyqtSignal('QString')

    def __init__(self):
        super().__init__()
        self.title = "LOCALBITCOIN AUTO SYSTEM"
        self.width = 1024
        self.height = 768
        self.initUI()
        self.initSingalSlot()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(self.width, self.height)

        self.isPricingStart = False
        self.isScrapingStart = False
        self.isSystemStart = False

        self.createTranactionTable()
        self.createPricingSection()
        self.createSellingSection()
        self.createScrapingSection()
        self.createSystemSection()
        self.createControlButtons()

        self.layoutMain = QVBoxLayout()
        self.layoutMain.addWidget(self.tableTranaction)
        self.layoutMain.addLayout(self.layoutPricing)
        self.layoutMain.addLayout(self.layoutSelling)
        self.layoutMain.addLayout(self.layoutScraping)
        self.layoutMain.addLayout(self.layoutSystem)
        self.layoutMain.addLayout(self.layoutButtons)
        self.setLayout(self.layoutMain)

    def initSingalSlot(self):
        self.btnPricing.clicked.connect(self.slot_OnClickBtnPricing)
        self.btnPayment.clicked.connect(self.slot_OnClickBtnPayment)
        self.btnScraping.clicked.connect(self.slot_OnClickBtnScraping)
        self.btnSystem.clicked.connect(self.slot_OnClickBtnSystem)
        self.btnExit.clicked.connect(self.slot_OnClickBtnExit)

    def createTranactionTable(self):
        self.tableTranaction = QTableWidget()
        self.tableTranaction.setColumnCount(6)
        self.tableTranaction.setHorizontalHeaderLabels(
            ['Created At', 'Trading Partner', 'Transaction Status', 'Fiat', 'Total BTC', 'Manual'])
        header = self.tableTranaction.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)

    def createPricingSection(self):
        self.layoutPricing = QHBoxLayout()
        self.labelPricing = QLabel('Pricing Status:')
        self.editPricing = QLineEdit('Ready...')
        self.editPricing.setStyleSheet('color: yellow')
        self.editPricing.setReadOnly(True)
        self.layoutPricing.addWidget(self.labelPricing)
        self.layoutPricing.addWidget(self.editPricing)
        self.layoutPricing.setStretch(0, 1)
        self.layoutPricing.setStretch(1, 7)

    def createSellingSection(self):
        self.layoutSelling = QHBoxLayout()
        self.labelSelling = QLabel('Selling Status:')
        self.editSelling = QLineEdit('Ready...')
        self.editSelling.setStyleSheet('color: yellow')
        self.editSelling.setReadOnly(True)
        self.layoutSelling.addWidget(self.labelSelling)
        self.layoutSelling.addWidget(self.editSelling)
        self.layoutSelling.setStretch(0, 1)
        self.layoutSelling.setStretch(1, 7)

    def createScrapingSection(self):
        self.layoutScraping = QHBoxLayout()
        self.labelScraping = QLabel('Scraping Status:')
        self.editScraping = QLineEdit('Ready...')
        self.editScraping.setStyleSheet('color: yellow')
        self.editScraping.setReadOnly(True)
        self.layoutScraping.addWidget(self.labelScraping)
        self.layoutScraping.addWidget(self.editScraping)
        self.layoutScraping.setStretch(0, 1)
        self.layoutScraping.setStretch(1, 7)

    def createSystemSection(self):
        self.layoutSystem = QHBoxLayout()
        self.labelSystem = QLabel('Pricing Status:')
        self.editSystem = QLineEdit('Ready...')
        self.editSystem.setStyleSheet('color: yellow')
        self.editSystem.setReadOnly(True)
        self.layoutSystem.addWidget(self.labelSystem)
        self.layoutSystem.addWidget(self.editSystem)
        self.layoutSystem.setStretch(0, 1)
        self.layoutSystem.setStretch(1, 7)

    def createControlButtons(self):
        self.layoutButtons = QHBoxLayout()
        self.btnPricing = QPushButton('START PRICING')
        self.btnPayment = QPushButton('PAYMENT DB')
        self.btnScraping = QPushButton('START SCRAPING')
        self.btnSystem = QPushButton('START SYSTEM')
        self.btnExit = QPushButton('EXIT')
        self.btnPricing.setStyleSheet('background-color: darkgreen')
        self.btnPayment.setStyleSheet('background-color: darkgreen')
        self.btnScraping.setStyleSheet('background-color: darkgreen')
        self.btnSystem.setStyleSheet('background-color: darkgreen')
        self.btnExit.setStyleSheet('background-color: darkred')
        self.layoutButtons.addWidget(self.btnPricing)
        self.layoutButtons.addWidget(self.btnPayment)
        self.layoutButtons.addWidget(self.btnScraping)
        self.layoutButtons.addWidget(self.btnSystem)
        self.layoutButtons.addWidget(self.btnExit)
        self.layoutButtons.setStretch(0, 1)
        self.layoutButtons.setStretch(1, 1)
        self.layoutButtons.setStretch(2, 1)
        self.layoutButtons.setStretch(3, 1)
        self.layoutButtons.setStretch(4, 1)

    # BUTTON CLICL EVENT FINCTIONS

    def slot_OnClickBtnPricing(self):
        if self.isPricingStart == False:
            self.btnPricing.setText('STOP PRICING')
            self.btnPricing.setStyleSheet('background-color: darkblue')
            self.isPricingStart = True
            self.buttonClickSignal.emit('START PRICING')
        else:
            self.btnPricing.setText('START PRICING')
            self.btnPricing.setStyleSheet('background-color: darkgreen')
            self.isPricingStart = False
            self.buttonClickSignal.emit('STOP PRICING')

    def slot_OnClickBtnPayment(self):
        self.buttonClickSignal.emit('PAYMENT DB')

    def slot_OnClickBtnScraping(self):
        if self.isScrapingStart == False:
            self.btnScraping.setText('STOP SCRAPING')
            self.btnScraping.setStyleSheet('background-color: darkblue')
            self.isScrapingStart = True
            self.buttonClickSignal.emit('START SCRAPING')
        else:
            self.btnScraping.setText('START SCRAPING')
            self.btnScraping.setStyleSheet('background-color: darkgreen')
            self.isScrapingStart = False
            self.buttonClickSignal.emit('STOP SCRAPING')

    def slot_OnClickBtnSystem(self):
        if self.isSystemStart == False:
            self.btnSystem.setText('STOP SYSTEM')
            self.btnSystem.setStyleSheet('background-color: darkblue')
            self.isSystemStart = True
            self.buttonClickSignal.emit('START SYSTEM')
        else:
            self.btnSystem.setText('START SYSTEM')
            self.btnSystem.setStyleSheet('background-color: darkgreen')
            self.isSystemStart = False
            self.buttonClickSignal.emit('STOP SYSTEM')

    def slot_OnClickBtnExit(self):
        self.buttonClickSignal.emit('EXIT')
