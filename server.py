from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import random
import requests
import json
from pymongo import MongoClient
import threading
from bson.objectid import ObjectId

def get_database():
   CONNECTION_STRING = "mongodb://localhost:27017"
   client = MongoClient(CONNECTION_STRING)
   return client['circe']
circe = get_database()
people = circe.people
readings = circe.readings

app = Flask(__name__)
api = Api(app)

class Search(Resource):
    def get(self, stri): 
        print(stri)
        fres= people.find({'name':{"$regex":'^'+stri,"$options":"i"}})
        res = [{"name":d["name"],"id":str(d["_id"]),"age":d["age"],"sessions":[str(x) for x in d["sessions"]]} for d in fres]
        return {"res":res} 

class Reading(Resource):
    def get(self, id):
        details = {}
        bp = {"sys":random.randint(90,140),"dia":random.randint(60, 90)}
        ecg = [random.randrange(150,250) for _ in range(188)]
        details.update({"bp":bp}) 
        details.update({"ecg":ecg})
        details.update({"temp":random.randrange(33,39)})
        details.update({"spo2":random.randrange(95,100)})
        details.update({"bpm":random.randrange(65,85)})
        def update_mongo(**kwargs):
            details = kwargs.get('details',{})
            x = readings.insert_one(details)
            people.update_one({"_id":ObjectId(id)},{'$push':{"sessions":x.inserted_id}})
        thread = threading.Thread(target=update_mongo,kwargs={'details':details.copy()}) 
        thread.start()
        print(details)
        return details

class Details(Resource):
    def get(self, id):
        x = readings.find_one({"_id":ObjectId(id)}) 
        res = {"id":id, "bp":x["bp"], "ecg":x["ecg"], "temp":x["temp"], "spo2":x["spo2"], "bpm":x["bpm"]}
        return res


api.add_resource(Search, '/search/<stri>')
api.add_resource(Reading, '/reading/<id>') 
api.add_resource(Details, '/details/<id>')
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5005,debug = True)