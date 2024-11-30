import sys
import json
from PyQt5.QtCore import *

from UI.MainWnd import MainWnd
from UI.PaymentView import PaymentView
from Pricing.PricingModule import PricingModule

class MainController(QObject):
    def __init__(self):
        super().__init__()

    def initialize(self):
        self.loadConfig()
        self.mainWnd = MainWnd()
        self.mainWnd.show()
        self.paymentView = PaymentView(self.paymentApiUrl)
        self.pricingModule = PricingModule(self.authKey, self.secretKey)
        self.initSignalSlot()

    def loadConfig(self):
        self.authKey = ''
        self.secretKey = ''
        try:
            with open("config.json") as config1:
                CONFIG = json.load(config1)
                self.authKey = CONFIG['auth_key']
                self.secretKey = CONFIG['secret_key']
                self.paymentApiUrl = CONFIG['PaymentApiUrl']
        except:
            print("Config File is not valid!")

    def initSignalSlot(self):
        self.mainWnd.buttonClickSignal.connect(self.slot_OnBtnClicked)
        self.pricingModule.signalPricing.connect(self.slot_Pricing)
        self.pricingModule.signalSelling.connect(self.slot_Selling)

    # SLOT FUNCTIONS
    def slot_OnBtnClicked(self, param):
        if param == 'START PRICING':
            self.pricingModule.start()
        if param == 'STOP PRICING':
            self.pricingModule.terminate()
        if param == 'PAYMENT DB':
            self.slot_PaymentDB()
        if param == 'EXIT':
            sys.exit()

    def slot_Pricing(self, param):
        self.mainWnd.editPricing.setText(param)

    def slot_Selling(self, param):
        self.mainWnd.editSelling.setText(param)

    def slot_PaymentDB(self):
        self.paymentView.show()

    def slot_Tranaction(self, param):
        self.mainWnd.editPricing.setText(param)
