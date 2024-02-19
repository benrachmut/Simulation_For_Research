import random
import abc

from abc import ABC

class Entity(ABC):

    def __init__(self):
        self.msgs_to_send = []

    @abc.abstractmethod
    def update_fields(self,id_list):
        return NotImplementedError

    @abc.abstractmethod
    def receive_msg(self):
        return NotImplementedError

    @abc.abstractmethod
    def compute(self):
        return NotImplementedError

    @abc.abstractmethod
    def send_msgs(self):
        return NotImplementedError


class Agent(Entity):
    def __init__(self,id_,tasks_ids):
        self.id_ = id_
        self.r_dict = {}
        self.x_dict = {}
        self.rnd = random.Random()
        self.rnd.seed(id_*17)
        self.bids_dict = {}

    def update_fields(self,id_list):
        for t in id_list:
            self.r_dict[t] = self.rnd.randint(0,100)
            self.x_dict[t] = 1

        for t in id_list:
            sigma_r = sum(self.r_dict.values())
            self.bids_dict[t] = self.r_dict[t]/sigma_r


class Task(Entity):

    def __init__(self,id_,tasks_ids):
        self.id_ = id_
        self.r_dict = {}
        self.x_dict = {}
        self.rnd = random.Random()
        self.rnd.seed(id_*17)
        self.bids_dict = {}

    def update_fields(self,id_list):
        for t in id_list:
            self.r_dict[t] = self.rnd.randint(0,100)
            self.x_dict[t] = 1

        for t in id_list:
            sigma_r = sum(self.r_dict.values())
            self.bids_dict[t] = self.r_dict[t]/sigma_r
