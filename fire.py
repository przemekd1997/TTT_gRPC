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
        print(users[0])
        n = random.randint(0,1)
        if n == 0:
            temp = users[0]
            x = users[0]
            y = user
        else:
            temp = user
            x = user
            y = users[0]

        ref.update({u'users': firestore.ArrayUnion([user]),
            u'x' : x,
            u'y' : y,
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
        data = ref.get().to_dict()
        x = data['x']
        y = data['y']
        board = data['board']
        win = 0
    
        if (board['00'] == 1 and board['11'] == 1 and board['22'] == 1):
            win = 1
        elif (board['00'] == 2 and board['11'] == 2 and board['22'] == 2):
            win = 2
        elif (board['02'] == 1 and board['11'] == 1 and board['20'] == 1):
            win = 1
        elif (board['02'] == 2 and board['11'] == 2 and board['20'] == 2):
            win = 2
        else:
            for i in range(3):
                scoreX1 = True
                scoreX2 = True
                scoreY1 = True
                scoreY2 = True
                for j in range(3):
                    s1 = str(i) + str(j)
                    s2 = str(j) + str(i)
                    scoreX1 = scoreX1 and (board[s1] == 1)
                    scoreX2 = scoreX2 and (board[s2] == 1)
                    scoreY1 = scoreY1 and (board[s1] == 2)
                    scoreY2 = scoreY2 and (board[s2] == 2)
            
                if(scoreX1 or scoreX2):
                    win = 1
                elif(scoreY1 or scoreY2):
                    win = 2
        

        refx = self.db.collection(u'users').document(x)
        refy = self.db.collection(u'users').document(y)
        datax = refx.get().to_dict()
        datay = refy.get().to_dict()

        nameX = datax['displayName']
        streakX = datax['currentWinStreak']
        winX = datax['wins']
        loseX = datax['loses']
        drawX = datax['draws']
        maxStreakX = datax['maxWinStreak']

        nameY = datay['displayName']
        streakY = datay['currentWinStreak']
        winY = datay['wins']
        loseY = datay['loses']
        drawY = datay['draws']
        maxStreakY = datay['maxWinStreak']

        matchX = {
                'enemy' : nameY,
                'enemyID' : y,
                'result' : 1 if win == 1 else 2 if win == 2 else 0
            }
    

        matchY = {
                'enemy' : nameX,
                'enemyID' : x,
                'result' : 1 if win == 2 else 2 if win == 1 else 0
            }

        if(win == 1):
            streakX += 1
            if(maxStreakX < streakX):
                maxStreakX = streakX
            streakY = 0
            refx.update({u'currentWinStreak': streakX,
                u'maxWinStreak' : maxStreakX,
                u'wins' : winX + 1,
                u'history': firestore.ArrayUnion([matchX])
            })
            refy.update({u'currentWinStreak': streakY,
                u'loses' : loseY + 1,
                u'history': firestore.ArrayUnion([matchY])
            })
        elif(win == 2):
            streakY += 1
            if(maxStreakY < streakY):
                maxStreakY = streakY
            streakY = 0
            refy.update({u'currentWinStreak': streakY,
                u'maxWinStreak' : maxStreakY,
                u'wins' : winY + 1,
                u'history': firestore.ArrayUnion([matchY])
            })
            refx.update({u'currentWinStreak': streakX,
                u'loses' : loseX + 1,
                u'history': firestore.ArrayUnion([matchX])
            })
        else:
            streakX = 0
            streakY = 0
            refx.update({u'currentWinStreak': streakX,
                u'draws' : drawX + 1,
                u'history': firestore.ArrayUnion([matchX])
            })
            refy.update({u'currentWinStreak': streakY,
                u'draws' : drawY + 1,
                u'history': firestore.ArrayUnion([matchY])
            })     
    
    
    def terminate(self,time):
        ref =  self.db.collection(u'games')
        query = ref.where(u'timestampStartGame', u'<=', time).get()

        for q in query:
            ref.document(q.id).delete()

base = Base("./titato-8a7f4-firebase-adminsdk-cacno-b118cf5928.json")
base.add_to_game("test2","test_doc")