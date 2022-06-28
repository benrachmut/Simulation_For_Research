import abc
import math
import random
from abc import ABC
import numpy as np

from simulation_abstract_components import Entity, PlayerSimple, TaskSimple


def quad_distance(entity1, entity2):
    l1 = entity1.location
    l2 = entity2.location

    delta_x_square = (l1[0] - l2[0]) ** 2
    delta_y_square = (l1[1] - l2[1]) ** 2
    quad_distance = math.sqrt(delta_x_square + delta_y_square)
    return quad_distance


class CommunicationProtocol(ABC):
    def __init__(self, is_with_timestamp, name):
        self.type_ = self.get_type()
        self.name = name
        self.is_with_timestamp = is_with_timestamp
        self.rnd = None
        self.rnd_numpy = None

    @abc.abstractmethod
    def copy_protocol(self):
        '''
        Delay/Loss/Perfect
        :return:
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def get_type(self):
        '''
        Delay/Loss/Perfect
        :return:
        '''
        raise NotImplementedError

    def __str__(self):
        return self.name

    def set_seed(self, seed):
        self.rnd = random.Random(seed)
        self.rnd_numpy = np.random.default_rng(seed=seed)

    def get_communication_disturbance(self, entity1: Entity, entity2: Entity):
        if isinstance(entity1, TaskSimple) and isinstance(entity2, PlayerSimple):
            if entity1.player_responsible.id_ == entity2.id_:
                return 0

        if isinstance(entity2, TaskSimple) and isinstance(entity1, PlayerSimple):
            if entity2.player_responsible.id_ == entity1.id_:
                return 0

        return self.get_communication_disturbance_by_protocol(entity1, entity2)

    @abc.abstractmethod
    def get_communication_disturbance_by_protocol(self, entity1: Entity, entity2: Entity):
        raise NotImplementedError

class CommunicationProtocolPerfectCommunication(CommunicationProtocol):
    def __init__(self):
        name = "PC"
        CommunicationProtocol.__init__(self, is_with_timestamp = False, name = name)

    def get_communication_disturbance_by_protocol(self, entity1: Entity, entity2: Entity):
        return 0


    def get_type(self):
        return "PC"

    def copy_protocol(self):

        return CommunicationProtocolPerfectCommunication()


class CommunicationProtocolDelayUniform(CommunicationProtocol):
    def __init__(self, is_with_timestamp, ub):
        self.ub = ub

        name = "U(0," + str(self.ub) + ")"
        CommunicationProtocol.__init__(self, is_with_timestamp, name)

    def get_communication_disturbance_by_protocol(self, entity1: Entity, entity2: Entity):
        return self.rnd_numpy.uniform(low=0.0, high=self.ub)


    def get_type(self):
        if self.ub  == 0:
            self.name = "PC"
            return "No Delay"
        else:
            return "Delay"

    def copy_protocol(self):
        is_with_time_stamp = self.is_with_time_stamp
        ub = self.ub
        return CommunicationProtocolDelayUniform(is_with_time_stamp,ub)

class CommunicationProtocolDelayPoisson(CommunicationProtocol):
    def __init__(self, is_with_timestamp, lambda_pois):
        self.lambda_pois = lambda_pois

        name = "Pois(" + str(self.lambda_pois) + ")"
        CommunicationProtocol.__init__(self, is_with_timestamp, name)

    def copy_protocol(self):
        is_with_time_stamp = self.is_with_time_stamp
        lambda_pois = self.lambda_pois
        return CommunicationProtocolDelayPoisson(is_with_time_stamp,lambda_pois)


    def get_communication_disturbance_by_protocol(self, entity1: Entity, entity2: Entity):
        return self.rnd_numpy.poisson(self.lambda_pois)

    def get_type(self):
        if self.lambda_pois  == 0:
            self.name = "PC"
            return "No Delay"
        else:
            return "Delay"

class CommunicationProtocolLossConstant(CommunicationProtocol):
    def __init__(self, p):
        name = "P=" + str(p)
        self.P = p
        CommunicationProtocol.__init__(self, name=name, is_with_timestamp=False)


    def get_communication_disturbance_by_protocol(self, entity1: Entity, entity2: Entity):
        p = self.rnd.random()
        if p < self.P:
            return 0
        else:
            return None


    def get_type(self):
        if self.P  == 0:
            self.name = "PC"
            return "No Loss"
        else:
            return "Loss"

    def copy_protocol(self):
        p = self.P
        return CommunicationProtocolLossConstant(p)

class CommunicationProtocolDistance(CommunicationProtocol):
    def __init__(self, name, alpha, delta_x, delta_y, is_with_timestamp):
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.alpha = alpha

        CommunicationProtocol.__init__(self, is_with_timestamp, name)


    def get_entity_quad_distance_rnd(self, entity1, entity2):
        return quad_distance(entity1, entity2)

    def normalize_distance(self, entity1, entity2):
        entity_quad_distance = self.get_entity_quad_distance_rnd(entity1, entity2)
        max_quad_distance = math.sqrt(self.delta_x ** 2 + self.delta_y ** 2)
        if entity_quad_distance > max_quad_distance:
            return 1
        return entity_quad_distance / max_quad_distance

class CommunicationProtocolLossExponent(CommunicationProtocolDistance):
    def __init__(self, alpha, delta_x, delta_y):
        name = "e^-(" + str(alpha) + "d)"
        CommunicationProtocolDistance.__init__(self, name=name, alpha=alpha, delta_x=delta_x, delta_y=delta_y,is_with_timestamp=False)

    def get_communication_disturbance_by_protocol(self, entity1: Entity, entity2: Entity):

        x = self.normalize_distance(entity1, entity2)
        P = math.exp(-self.alpha * x)
        p = self.rnd.random()
        if p < P:
            return 0
        else:
            return None

    def get_type(self):
        if self.alpha == 0:
            self.name = "PC"
            return "No Loss"
        else:
            return "Loss"

    def copy_protocol(self):
        delta_x = self.delta_x
        delta_y = self.delta_y
        alpha = self.alpha
        return CommunicationProtocolLossExponent(delta_x =delta_x,delta_y =delta_y,alpha = alpha)

class CommunicationProtocolDelayDistancePoissonExponent(CommunicationProtocolDistance):
    def __init__(self, alpha, delta_x, delta_y, is_with_timestamp):

        name = "Pois(" + str(alpha) + "^d)"
        CommunicationProtocolDistance.__init__(self, name=name, alpha=alpha, delta_x=delta_x, delta_y=delta_y,is_with_timestamp =is_with_timestamp)

    def get_communication_disturbance_by_protocol(self, entity1: Entity, entity2: Entity):

        x = self.normalize_distance(entity1, entity2)
        lamb = self.alpha ** x
        ans = self.rnd_numpy.poisson(lamb)

        return ans

    def get_type(self):
        if self.alpha == 0:
            return "No Delay"
        else:
            return "Delay"

    def copy_protocol(self):
        delta_x = self.delta_x
        delta_y = self.delta_y
        alpha = self.alpha
        time_stamp = self.is_with_timestamp
        return CommunicationProtocolDelayDistancePoissonExponent(delta_x =delta_x,delta_y =delta_y,alpha = alpha,is_with_timestamp =time_stamp)

class CommunicationProtocolDelayDistanceUniformExponent(CommunicationProtocolDistance):
    def __init__(self, alpha, delta_x, delta_y, is_with_timestamp):

        name = "U(0," + str(alpha) + "^d)"
        CommunicationProtocolDistance.__init__(self, name=name, alpha=alpha, delta_x=delta_x, delta_y=delta_y,is_with_timestamp = is_with_timestamp)

    def get_communication_disturbance_by_protocol(self, entity1: Entity, entity2: Entity):

        x = self.normalize_distance(entity1, entity2)
        UB = self.alpha ** x
        ans = self.rnd_numpy.uniform(low=0.0, high=UB)

        return ans

    def get_type(self):
        if self.alpha == 0:
            self.name ="PC"
            return "No Delay"
        else:
            return "Delay"


    def copy_protocol(self):
        delta_x = self.delta_x
        delta_y = self.delta_y
        alpha = self.alpha
        time_stamp = self.is_with_timestamp
        return CommunicationProtocolDelayDistanceUniformExponent(delta_x =delta_x,delta_y =delta_y,alpha = alpha,is_with_timestamp =time_stamp)

def get_communication_protocols(width, length, is_with_timestamp, is_with_perfect_communication = True,
                                constants_loss_distance=[],
                                constants_loss_constant=[],

                                constants_delay_poisson_distance=[],
                                constants_delay_poisson=[],
                                constants_delay_uniform_distance=[],
                                constants_delay_uniform=[]

                                ):
    ans = []

    if is_with_perfect_communication:
        ans.append(CommunicationProtocolPerfectCommunication())

    for a in constants_loss_distance:
        ans.append(CommunicationProtocolLossExponent(alpha=a, delta_x=width, delta_y=length
                                                     ))

    for p in constants_loss_constant:
        ans.append(CommunicationProtocolLossConstant(p=p))

    for b in constants_delay_poisson_distance:
        ans.append(CommunicationProtocolDelayDistancePoissonExponent(alpha=b, delta_x=width, delta_y=length,
                                                                     is_with_timestamp=is_with_timestamp))

    for b_ub in constants_delay_uniform_distance:
        ans.append(CommunicationProtocolDelayDistanceUniformExponent(alpha=b_ub, delta_x=width, delta_y=length,
                                                                     is_with_timestamp=is_with_timestamp))

    for lam in constants_delay_poisson:
        ans.append(CommunicationProtocolDelayPoisson(is_with_timestamp, lam))

    for ub in constants_delay_uniform:
        ans.append(CommunicationProtocolDelayUniform(is_with_timestamp, ub))

    return ans