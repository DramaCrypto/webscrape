from flask import Flask, request
from flask_restful import Resource, Api
from pymongo import MongoClient

client = MongoClient(port=27018)
db = client.payment_db
app = Flask(__name__)
api = Api(app)

class Tranaction(Resource):
    def get(self):
        return "Thank you for your visit!"

    def post(self):
        try:
            if request.json["Account_TransactionOwnerName"] == "ELEMENT TRADERS LTD-MA":
                return
            print(request.json)
            result = db.tranactions.insert_one(request.json)
        except:
            print('Tranaction Post Process Failed!')

class GetAllTranaction(Resource):
    def get(self):
        all = db.tranactions.find()
        all_list = []
        for x in all:
            tranaction = {
                "CounterpartAccount_TransactionOwnerName": x["CounterpartAccount_TransactionOwnerName"],
                "Amount": x["Amount"],
                "Reference": x["Reference"],
                "TimestampSettled": x["TimestampSettled"],
            }
            all_list.append(tranaction)
        return all_list

class DelAllTranaction(Resource):
    def get(self):
        try:
            result = db.tranactions.remove()
            return 'SUCCESS'
        except:
            return 'FAILED'

api.add_resource(Tranaction, '/tranaction')
api.add_resource(GetAllTranaction, '/get-all-tranaction')
api.add_resource(DelAllTranaction, '/del-all-tranaction')

if __name__ == '__main__':
    app.run(host='www.ysrtraders.com', port='5002', debug=False)
