from abc import ABC, abstractmethod


class NavStrategy(ABC):

    def  __init__(self, robots, environment):
        self.robots = robots
        self.env = environment

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def extract_data(self):
        pass
