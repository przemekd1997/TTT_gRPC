import firebase_admin
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
        ref.update({u'users': firestore.ArrayUnion([user]),
            u'timestampStartGame' : datetime.datetime.now()})
        
