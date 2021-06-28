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
        u'board': {
            u'00' : 0,
            u'01' : 0,
            u'02' : 0,
            u'10' : 0,
            u'11' : 0,
            u'12' : 0,
            u'20' : 0,
            u'21' : 0,
            u'22' : 0
        },
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

    def fin_check(self,game):
        ref = self.db.collection(u'games').document(game)
        fin = ref.get()
        if (fin.exists):
            fin = fin.to_dict()
            fin = fin['isFinished']

            if (fin == False):
                ref.update({u'isFinished': True})
                return 1
            else:
                return 0
        else:
            return -1

    def finalize(self,game):
        ref =  self.db.collection(u'games').document(game)
        users = ref.get().to_dict()
        users = users['users']

        for u in users:
            usr = self.db.collection(u'users').document(u)
    
    def terminate(self,time):
        ref =  self.db.collection(u'games')
        query = ref.where(u'timestampStartGame', u'<=', time).get()

        for q in query:
            ref.document(q.id).delete()