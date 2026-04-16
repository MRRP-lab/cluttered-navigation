import socket
import src.protobuf.multiagent_pathfinding_protobuf.problem_pb2 as problem

from src.strategies.navstrategy import NavStrategy

# The optimal strategy leverages the optimal solution java server, and assumes that it's running.
class OptimalStrategy(NavStrategy):
    ip = "localhost"
    port = 55555

    def __init__(self, robots, env):
        super().__init__(robots, env)
        self.data = []
        self.adj_list, self.sinks = self.env.to_adj_matrix_with_supersinks(self.robots.num)

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((OptimalStrategy.ip, OptimalStrategy.port))
        
        protobuf = self.populate_protobuf()
        
        message = protobuf.SerializeToString()
        self.socket.sendall(message)
        self.socket.shutdown(socket.SHUT_WR)

        # wait for a response to be completed...
        resp = b""
        while chunk := self.socket.recv(4096):
            resp += chunk
        self.socket.close()
        solution_resp = problem.Solution()
        solution_resp.ParseFromString(resp)

        self.produce_data_from_solution(solution_resp)

    def populate_protobuf(self):
        self.adj_list
        
        problem_proto = problem.Instance()
        for node in list(self.adj_list.values()) + self.sinks:
            node_proto = problem_proto.nodes.add()
            node_proto.id = node.id
            for neighbor in node.neighbors:
                node_proto.neighbors.append(neighbor.id)

        robot_id = 0
        for c in self.robots.coords:
            assignment_proto = problem_proto.assignments.add()

            assignment_proto.robot_id = robot_id
            assignment_proto.finish_id = self.sinks[robot_id].id
            # c is stored as a numpy array, turn it to a tuple before using it in the dict
            assignment_proto.start_id = self.adj_list[(int(c[0]), int(c[1]))].id

            robot_id += 1
        if (len(self.adj_list) > 10000):
            print("WARNING: attempting to use centralized solver on graph with >10000 nodes which isn't supported by the solver!")
        return problem_proto

    def produce_data_from_solution(self, solution_msg):
        # We need to cross-reference node IDs to get x and y coordinates.
        nodes_by_id = {}
        for node in list(self.adj_list.values()) + self.sinks:
            nodes_by_id[node.id] = node

        # If the robots reach the finish (when x and y are None), they stay in the same spot.
        prev_coords = {}
        for timestep in solution_msg.timesteps:
            for pos in timestep.positions:
                node = nodes_by_id[pos.node_id]
                x = node.x
                y = node.y
                if x is None or y is None:
                    x = prev_coords[pos.robot_id][0]
                    y = prev_coords[pos.robot_id][1]

                self.data.append([
                    timestep.time,
                    pos.robot_id,
                    x,
                    y
                    ])
                prev_coords[pos.robot_id] = (x, y)

    def extract_data(self):
        return self.data

