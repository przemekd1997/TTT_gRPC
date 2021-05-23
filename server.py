from fire import Base
from concurrent import futures
import grpc
import ttt_service_pb2
import ttt_service_pb2_grpc
import time
import datetime
import threading

free_games = []
base = Base("./titato-8a7f4-firebase-adminsdk-cacno-b118cf5928.json")

class Listener(ttt_service_pb2_grpc.TTTServicer):
    def __init__(self):
        self.data_base = base
        self.lock = threading.Lock()

    def JoinMatchmaking(self, request, context): 
        global free_games
        uid = request.id
        yield ttt_service_pb2.HandShake()
        if (len(free_games) == 0):
            name = self.data_base.create_game(uid,True)
            with self.lock:
                free_games.append(name)
            print("czekam na gre: " + str(uid))
            while True:
                if not context.is_active():
                    with self.lock:
                        free_games.remove(name)
                    self.data_base.remove_game(name)
                    return
                if name not in free_games:
                    break
            print("znalazlem gre: " + str(uid))
        else:
            with self.lock:
                name = free_games.pop(0)
            print("dolaczylem sie: " + str(uid))
            self.data_base.add_to_game(uid,name)
        game = ttt_service_pb2.Game(id = name)
        yield game
    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    timest = datetime.datetime.now()
    ts = timest.strftime("%Y-%m-%d %H:%M:%S")
    t = datetime.datetime.strptime(ts,"%Y-%m-%d %H:%M:%S")

    ttt_service_pb2_grpc.add_TTTServicer_to_server(Listener(), server)
    server.add_insecure_port('[::]:9999')
    server.start()
    try:
        while True:
            times1 = datetime.datetime.now()
            ts1 = times1.strftime("%Y-%m-%d %H:%M:%S")
            t1 = datetime.datetime.strptime(ts1,"%Y-%m-%d %H:%M:%S")
            dif = t - t1
            if(dif.seconds >= 3600):
                base.terminate(timest)
                timest = ts1
                print("games deleted")
            print("server active: on threads %i" % (threading.active_count()))
            time.sleep(10)
    except KeyboardInterrupt:
        print("keyboard interrupt")
        server.stop(0)

if __name__ == "__main__":
    serve()