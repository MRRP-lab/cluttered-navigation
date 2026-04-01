import socket
import src.protobuf.multiagent_pathfinding_protobuf.problem_pb2 as problem

from src.strategies.navstrategy import NavStrategy

# The optimal strategy leverages the optimal solution java server, and assumes that it's running.
class OptimalStrategy(NavStrategy):
    ip = "localhost"
    port = 55555

    def __init__(self, robots, env):
        super().__init__(robots, env)

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((OptimalStrategy.ip, OptimalStrategy.port))
        assignment_msg = problem.Assignment()
        assignment_msg.robot_id = 100
        assignment_msg.start_id = 123
        assignment_msg.finish_id = 500

        message = assignment_msg.SerializeToString()
        self.socket.sendall(message)
        self.socket.shutdown(socket.SHUT_WR)

        # wait for a response to be completed...
        resp = b""
        while chunk := self.socket.recv(4096):
            resp += chunk
        self.socket.close()
        assignment_resp = problem.Assignment()
        assignment_resp.ParseFromString(resp)

        print(f"Python: {assignment_resp.robot_id}")
        print(f"Python: {assignment_resp.start_id}")
        print(f"Python: {assignment_resp.finish_id}")


    def extract_data(self):
        pass

