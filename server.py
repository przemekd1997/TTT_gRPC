from fire import Base
import grpc
import ttt_service_pb2
import ttt_service_pb2_grpc

class Listener(ttt_service_pb2_grpc.TTTServicer):
    def __init__(self):
        self.free_games = []
        self.data_base = Base("./titato-8a7f4-firebase-adminsdk-cacno-b118cf5928.json")

    def JoinMatchmaking(self, request, context): 
        uid = request.id
        if (len(free_games) == 0):
            name = data_base.create_game(uid,True)
            self.free_games.append(name)
        else:
            name = self.free_games.pop(0)
            data_base.add_to_game(uid,name)
        game = ttt_service_pb2.Game(id = name)
        self.free_games.append(game)
        yield game