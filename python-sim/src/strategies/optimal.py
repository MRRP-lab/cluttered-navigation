import socket

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
        # wait for a response and for the socket to be closed. Yield in the meantime.
        pass

    def extract_data(self):
        pass
