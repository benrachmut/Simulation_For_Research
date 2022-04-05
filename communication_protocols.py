import abc
import math
import random
from abc import ABC
import numpy as np

from simulation_abstract_components import Entity, PlayerSimple, TaskSimple

def quad_distance(entity1,entity2):
    l1 =entity1.location
    l2 =entity2.location

    delta_x_square = (l1[0] - l2[0]) ** 2
    delta_y_square = (l1[1] - l2[1]) ** 2
    quad_distance = math.sqrt(delta_x_square + delta_y_square)
    return quad_distance

class CommunicationProtocol(ABC):
    def __init__(self, is_with_timestamp, name):

        self.name = name
        self.is_with_timestamp = is_with_timestamp
        self.rnd = None
        self.rnd_numpy = None

    def __str__(self):
        return self.name

    def set_seed(self, seed):
        self.rnd = random.Random(seed)
        self.rnd_numpy = np.random.default_rng(seed=seed)

    def get_communication_disturbance(self, entity1: Entity, entity2: Entity):
        if isinstance(entity1, TaskSimple) and isinstance(entity2,PlayerSimple):
            if entity1.player_responsible.id_ == entity2.id_:
                return 0

        if isinstance(entity2, TaskSimple) and isinstance(entity1, PlayerSimple):
            if entity2.player_responsible.id_ == entity1.id_:
                return 0

        return self.get_communication_disturbance_by_protocol(entity1, entity2)

    @abc.abstractmethod
    def get_communication_disturbance_by_protocol(self, entity1: Entity, entity2: Entity):
        raise NotImplementedError

class CommunicationProtocolDistance(CommunicationProtocol):
    def __init__(self, name,alpha,delta_x,delta_y,std = 10, is_with_timestamp=False):
        CommunicationProtocol.__init__(self, is_with_timestamp, name)

        self.delta_x = delta_x
        self.delta_y = delta_y
        self.alpha = alpha
        self.std = std



    def get_entity_quad_distance_rnd(self,entity1,entity2):
        avg = quad_distance(entity1,entity2)
        return max(self.rnd_numpy.normal(avg, self.std, 1)[0],0)

    def normalize_distance(self,entity1,entity2):
        entity_quad_distance = self.get_entity_quad_distance_rnd(entity1, entity2)
        max_quad_distance = math.sqrt(self.delta_x**2 + self.delta_y**2)
        if entity_quad_distance>max_quad_distance:
            raise Exception("something is wrong")
        return entity_quad_distance/max_quad_distance

class CommunicationProtocolLossExponent(CommunicationProtocolDistance):
    def __init__(self, alpha, delta_x, delta_y, std = 10):
        name = "e^-("+str(alpha)+"x)"
        CommunicationProtocolDistance.__init__(self,name = name, alpha =alpha, delta_x=delta_x, delta_y=delta_y, std=std )


    def get_communication_disturbance_by_protocol(self, entity1: Entity, entity2: Entity):

        x = self.normalize_distance(entity1,entity2)
        P = math.exp(-self.alpha*x)
        p = self.rnd.random()
        if p<P:
            return 0
        else:
            return None

class CommunicationProtocolDelayExponent(CommunicationProtocolDistance):
    def __init__(self, alpha, delta_x, delta_y, std = 10):
        name = "x^"+str(alpha)

        CommunicationProtocolDistance.__init__(self,name = name, alpha =alpha, delta_x=delta_x, delta_y=delta_y, std=std )

    def get_communication_disturbance_by_protocol(self, entity1: Entity, entity2: Entity):
        x = self.normalize_distance(entity1,entity2)
        return self.alpha ** x
