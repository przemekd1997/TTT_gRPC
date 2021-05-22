#python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./ttt_service.proto 
import firebase_admin
import random
from firebase_admin import credentials
from firebase_admin import firestore
import datetime

class Base:
    def __init__(self, file):
        self.cred = credentials.Certificate(file)
        self.default_app = firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()


    def create_game(self,user,join):
        ref =  self.db.collection(u'games').document()
        data = {
        u'joinable' : join,
        u'users': [user],
        u'score': 0,
        u'timestampStartGame': datetime.datetime.now(),
        u'turn': user,
        u'isFinished': False
        }
        ref.set(data)
        return ref.id

    def add_to_game(self,user,game):
        ref =  self.db.collection(u'games').document(game)
        users = ref.get().to_dict()
        users = users['users']
        n = random.randint(0,1)
        if n == 0:
            temp = users[0]
        else:
            temp = user

        ref.update({u'users': firestore.ArrayUnion([user]),
            u'turn': temp,
            u'timestampStartGame' : datetime.datetime.now()})
    
    def remove_game(self,game):
        ref =  self.db.collection(u'games').document(game)
        ref.delete()