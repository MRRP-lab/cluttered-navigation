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
        
        protobuf = self.populate_protobuf()
        
        message = protobuf.SerializeToString()
        self.socket.sendall(message)
        self.socket.shutdown(socket.SHUT_WR)

        # wait for a response to be completed...
        resp = b""
        while chunk := self.socket.recv(4096):
            resp += chunk
        self.socket.close()
        assignment_resp = problem.Assignment()
        assignment_resp.ParseFromString(resp)

    def populate_protobuf(self):
        adj_list, sinks = self.env.to_adj_matrix_with_supersinks(self.robots.num)

        problem_proto = problem.Instance()
        for node in list(adj_list.values()) + sinks:
            node_proto = problem_proto.nodes.add()
            node_proto.id = node.id
            for neighbor in node.neighbors:
                node_proto.neighbors.append(neighbor.id)

        robot_id = 0
        for c in self.robots.coords:
            assignment_proto = problem_proto.assignments.add()

            assignment_proto.robot_id = robot_id
            assignment_proto.finish_id = sinks[robot_id].id
            # c is stored as a numpy array, turn it to a tuple before using it in the dict
            assignment_proto.start_id = adj_list[(int(c[0]), int(c[1]))].id

            robot_id += 1

        return problem_proto

    def extract_data(self):
        pass

