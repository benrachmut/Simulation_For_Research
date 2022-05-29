import abc
import copy
import enum
import random
from abc import ABC
import numpy as np

travel_factor = 0.9
travel_factor_normalized = 1000
length_  = None
width_ = None



class MapSimple:
    """
    Class that represents the map for the simulation. The tasks and the players must be located using generate_location
    method. The simple map is in the shape of rectangle (with width and length parameters).
    """

    def __init__(self, seed=1, length=900.0, width=900.0):
        """
        :param number_of_centers: number of centers in the map. Each center represents a possible base for the player.
        :type: int
        :param seed: seed for random object
        :type: int
        :param length: The length of the map
        :type: float
        :param width: The length of the map
        :type: float
        """
        self.length = length
        self.width = width
        global length_
        length_ = length

        global width_
        width_ = width


        self.rand = random.Random(seed)


    def generate_location(self):
        """
        :return: random location on the map
        :rtype: list of float
        """
        x1 = self.rand.random()
        x2 = self.rand.random()
        return [self.width * x1, self.length * x2]


    def get_the_center_of_the_map_location(self):
        return [self.width/2,self.length/2]




class TaskGenerator(ABC):
    def __init__(self, map_=MapSimple(seed=1), seed=1):
        """

        :param map_:
        :param seed:
        """
        self.map = map_
        self.random = random.Random(seed)
        self.rnd_numpy = np.random.default_rng(seed=seed)

    @abc.abstractmethod
    def get_task(self, tnow):
        """
        :rtype: TaskSimple
        """
        return NotImplementedError

    @abc.abstractmethod
    def time_gap_between_tasks(self):
        return NotImplementedError

class Status(enum.Enum):
    """
    Enum that represents the status of the player in the simulation
    """
    IDLE = 0
    ON_MISSION = 1
    TO_MISSION = 2

class SimpleTaskGenerator(TaskGenerator):
    def __init__(self, max_number_of_missions ,map_, seed, players_list,are_neighbors_f,max_importance=10):
        """

        :param map_: object to initiate location
        :param seed: used for randomization
        :param factor_initial_workload: initial_workload = self.factor_initial_workload**task_importance
        :param max_importance: the maximum level of importance
        :param exp_lambda_parameter: used to get random gap between tasks exp(exp_lambda_parameter)
        """
        TaskGenerator.__init__(self, map_, seed)
        self.id_task_counter = 1
        self.id_mission_counter = 1
        self.max_importance = max_importance
        self.max_number_of_missions =  max_number_of_missions
        self.players_list = players_list
        self.skill_range =  []
        for skill_number in range(self.max_number_of_missions):
            self.skill_range.append(skill_number)
        self.are_neighbors_f = are_neighbors_f

    def time_gap_between_tasks(self):
        return self.rnd_numpy.exponential(scale=self.beta, size=1)[0]

    def get_task(self, tnow,flag_time_zero = False):
        """
        :rtype: TaskSimple
        """

        #amount_of_missions = self.random.randint(1, self.max_number_of_missions)
        required_abilities = self.skill_range#self.random.sample(self.skill_range ,amount_of_missions)
        self.id_task_counter = self.id_task_counter + 1
        id_ = str(self.id_task_counter)
        location = self.map.generate_location()# #self.map.generate_location()
        importance = (self.random.random() * self.max_importance)
        if flag_time_zero:
            arrival_time = tnow
        else:
            arrival_time = tnow + self.time_gap_between_tasks()
        missions_list = []
        for ability in required_abilities:
            mission_created = self.create_random_mission(task_id=id_,task_importance=importance, arrival_time=arrival_time,ability = ability)
            missions_list.append(mission_created)


        task = TaskSimple(id_=id_, location=location, importance=importance,
                          missions_list=missions_list, arrival_time=arrival_time)


        task.neighbours = self.get_neighbors_ids(task,missions_list)
        return task

    def get_neighbors_ids(self,task,missions_list):
        player_ids = []
        skills_list  = []
        for mission in missions_list:
            for ability in mission.abilities:
                skills_list.append(ability)
        for player in self.players_list:
            for ability in player.abilities:
                if ability in skills_list:
                    if self.are_neighbors_f(task,player):
                        player_ids.append(player.id_)
        # player_responsible = task.player_responsible
        # if player_responsible.id_ not in player_ids:
        #     player_ids.append(player_responsible)

        return player_ids

    def get_tasks_number_of_tasks_now(self, tnow,number_of_tasks):
        ans = []
        for _ in range(number_of_tasks):
            ans.append(self.get_task(tnow = tnow,flag_time_zero = True))
        return ans

    def create_random_mission(self, task_id,task_importance: float, arrival_time: float,ability):
        created_ability = AbilitySimple(ability_type=ability)
        self.id_mission_counter = self.id_mission_counter + 1
        mission_id = str(self.id_mission_counter)
        initial_workload = task_importance*100000

            #task_importance*10000#self.rnd_numpy.poisson(lam=(task_importance), size=1)[0]#self.random.uniform(task_importance,task_importance*2)#self.factor_initial_workload ** (task_importance/1000)
        arrival_time_to_the_system = arrival_time

        rnd_ = max(2,round(self.random.uniform(1,task_importance)))
        max_players = min(rnd_,10)

        return MissionSimple(task_id =task_id,task_importance = task_importance,mission_id= mission_id,
                             initial_workload= initial_workload, arrival_time_to_the_system= arrival_time_to_the_system, max_players=max_players,abilities=[created_ability])

class AbilitySimple:
    """
       Class that represents a simple ability that the missions require and the players have
    """

    def __init__(self, ability_type, ability_name=None):
        """
        :param ability_type: The type of the ability
        :type ability_type: int
        :param ability_name: The name of the ability. If the name is not given it will be set to the type of the ability
        (casted to str)
        :type ability_name: str
        """

        self.ability_type = ability_type
        self.ability_name = ability_name
        if self.ability_name is None:
            self.ability_name = str(ability_type)

    def __hash__(self):
        return hash(self.ability_type)

    def __eq__(self, other):
        return self.ability_type == other.ability_type

    def __str__(self):
        return self.ability_name

    def get_ability_type(self):
        return self.ability_type

class Entity:
    """
    Class that represents a basic entity in the simulation
    """

    def __init__(self, id_, location, last_time_updated=0):
        """
        :param id_: The id of the entity
        :type  id_: str
        :param location: The location of the entity. A list of of coordination.
        :type location: list of floats
        :param last_time_updated:

        """
        self.id_ = id_
        self.location = location
        self.neighbours = []
        self.last_time_updated = last_time_updated

    def update_time(self, tnow):
        if tnow >= self.last_time_updated:
            self.last_time_updated = tnow
        #else:
        #    raise Exception("last time updated is higher than tnow")

    def create_neighbours_list(self, entities_list: list, f_are_neighbours):
        """
        Method that populates the neighbours list of the entity. It accepts list of potential neighbours
        and a function that returns whether a pair of entities are neighbours
        :param entities_list: List of entities that are potential neighbours
        :type entities_list: list ot Entity
        :param f_are_neighbours: Function that receives 2 entities and return true if they can be neighbours
        :type f_are_neighbours: function
        :return: None
        """
        raise NotImplementedError

    def __hash__(self):
        return hash(self.id_)

    def __eq__(self, other):
        return self.id_ == other.id_

    def __str__(self):
        return str(self.id_)

def calculate_distance_input_location(location1, location2):
    """
    Calculates the distance between two entities. Each entity must have a location property.
    :param location1:first location
    :type location1: list
    :param location2:second location
    :type location2: list
    :return: Euclidean distance between two entities
    :rtype: float
    """

    distance = 0
    n = min(len(location1), len(location2))
    for i in range(n):
        distance += (location1[i] - location2[i]) ** 2

    return distance ** 0.5

def calculate_distance(entity1: Entity, entity2: Entity):
    """
    Calculates the distance between two entities. Each entity must have a location property.
    :param entity1:first entity
    :type entity1: Entity
    :param entity2:second entity
    :type entity1: Entity
    :return: Euclidean distance between two entities
    :rtype: float
    """
    location1 = entity1.location
    location2 = entity2.location
    return calculate_distance_input_location(location1, location2)

class PlayerSimple(Entity):
    """
    Class that represents a basic player in the simulation
    """

    def __init__(self, id_, current_location, speed, status=Status.IDLE,
                 abilities=None, tnow=0, base_location=None, productivity=1):
        """
        :param id_: The id of the player
        :type  id_: str
        :param current_location: The location of the player
        :type current_location: list of float
        :param status: The status of the player
        :type  status: Status
        :param abilities: abilities of the player
        :type  abilities: set of AbilitySimple
        :param current_task: The current task that was allocated to player. If the the player is idle this field will be None.
        :type current_task: TaskSimple
        :param current_mission: The current sub-task of the player. If the the player is idle this field will be None.
        :type current_mission: MissionSimple

        """
        Entity.__init__(self, id_, current_location, tnow)
        if abilities is None:
            abilities = [AbilitySimple(ability_type=0)]
        self.speed = speed
        self.status = status
        self.abilities = abilities
        self.current_task = None
        self.current_mission = None
        self.tasks_responsible = []
        self.neighbours = []
        self.base_location = base_location
        self.productivity = productivity
        self.schedule = []  # [(task,mission,time)]

    def update_status(self, new_status: Status, tnow: float) -> None:
        """
        Updates the status of the player
        :param new_status:the new status of the player
        :param tnow: the time when status of the player is updated
        :return:None
        """
        self.status = new_status
        self.update_time(tnow)

    def update_location(self, location, tnow):
        """
        Updates the location of the player
        :param location:
        :param tnow:
        :return:
        """
        self.location = location
        self.update_time(tnow)

    # def create_neighbours_list(self, players_list, f_are_neighbours=are_neighbours):
    #     """
    #     creates neighbours list of players
    #     :param players_list:
    #     :param f_are_neighbours:
    #     :return:None
    #     """
    #     for p in players_list:
    #         if self.id_ != p.id_ and f_are_neighbours(self, p):
    #             self.neighbours.append(p)

    def calculate_relative_location(self, tnow):
        if self.status == Status.TO_MISSION:
            travel_time = calculate_distance(self, self.current_task) / self.speed
            time_delta = tnow - self.last_time_updated
            ratio_of_the_time = time_delta / travel_time
            for i in range(len(self.location)):
                self.location[i] = self.location[i] + (
                        self.current_task.location[i] - self.location[i]) * ratio_of_the_time
            self.update_time(tnow)

def is_player_can_be_allocated_to_task(task, player):
    """
    Function that checks if the player can be allocated to an task according to player's abilities and required abilities
    to the task.
    :param task: The task that is checked.
    :type task: TaskSimple
    :param player: The player that is checked if it suitable for the task according to hos abilities.
    :return:
    """
    # for mission in task.missions_list:
    #    for ability in mission.abilities:
    #        if ability in player.abilities:
    #            return True
    return True

class MissionMeasurements:
    def __init__(self, task_id, task_importance, mission_id, arrival_time_to_the_system, initial_workload, max_players):
        self.task_id = task_id
        self.task_importance = task_importance
        self.mission_id = mission_id
        self.max_players = max_players
        self.x0_simulation_time_mission_enter_system = copy.copy(arrival_time_to_the_system)
        self.x1_simulation_time_first_player_arrive = None  # update when mission finish
        self.x2_delay = None

        self.x3_abandonment_counter = 0  # each decrease in players present
        self.x4_total_abandonment_counter = 0  # decrease from 1 to 0
        self.x5_simulation_time_mission_end = None
        self.x6_total_time_since_arrive_to_system = None
        self.x7_total_time_since_first_agent_arrive = None

        self.initial_workload = initial_workload
        self.max_players = max_players
        self.x8_optimal_time = initial_workload / max_players
        self.x9_ratio_time_taken_arrive_to_system_and_opt = None
        self.x10_ratio_time_taken_first_agent_arrive_and_opt = None

        self.x11_time_per_quantity_time_in_system = self.create_dict_of_players_amounts()
        self.x12_workload_per_quantity_time_in_system = self.create_dict_of_players_amounts()

        self.x13_time_per_quantity_time_first_player = self.create_dict_of_players_amounts()
        self.x14_workload_per_quantity_time_first_player = self.create_dict_of_players_amounts()

        self.x16_workload_utility_without_zero = None
        self.x17_workload_utility_with_zero = None

        self.x20_abandonment_penalty = 0

        self.players_allocated_to_the_mission_previous = []
        self.players_handling_with_the_mission_previous = []
        self.is_mission_done = True

    def get_mission_measurements_dict(self):
        ans = {}
        ans["Task Id"] = self.task_id

        ans["Mission Id"] = self.mission_id
        ans["Task Importance"] = self.task_importance
        ans["Max Players"] = self.max_players
        ans["Initial Workload"] = self.initial_workload
        ans["Arrival Delay"] = self.x2_delay
        ans["Abandonment Counter"] = self.x3_abandonment_counter
        ans["Total Abandonment Counter"] = self.x4_total_abandonment_counter
        ans["Total Time In System"] = self.x6_total_time_since_arrive_to_system
        ans["Total Time Since First Arrival"] = self.x7_total_time_since_first_agent_arrive
        ans["Time Taken (In System) Relative To Optimal"] = self.x9_ratio_time_taken_arrive_to_system_and_opt
        ans["Time Taken (First Arrival) Relative To Optimal"] = self.x10_ratio_time_taken_first_agent_arrive_and_opt
        ans["Cap"] = self.x16_workload_utility_without_zero

        ans["Is Done"] = self.is_mission_done
        ans["Abandonment Penalty"]  = self.x20_abandonment_penalty
        if isinstance(ans["Cap"],float) and isinstance(ans["Arrival Delay"],float):
            ans["Utility"] = ans["Cap"] * (travel_factor**(ans["Arrival Delay"]/travel_factor_normalized)) - ans["Abandonment Penalty"]
        else:
            ans["Utility"] = 0
        return ans

    def close_measurements(self):

        if self.x2_delay is None:
            self.x2_delay = "NaN"

        if self.x6_total_time_since_arrive_to_system is None:
            self.x6_total_time_since_arrive_to_system = "NaN"

        if self.x7_total_time_since_first_agent_arrive is None:
            self.x7_total_time_since_first_agent_arrive = "NaN"

        if self.x10_ratio_time_taken_first_agent_arrive_and_opt is None:
            self.x10_ratio_time_taken_first_agent_arrive_and_opt = "NaN"

        if self.x10_ratio_time_taken_first_agent_arrive_and_opt is None:
            self.x10_ratio_time_taken_first_agent_arrive_and_opt = "NaN"

        self.calculate_mission_utility()
        self.is_mission_done = False

    def change_abandonment_measurements(self, player,current_task,current_mission):

        remaining_workload_ratio = current_mission.remaining_workload / current_mission.initial_workload
        abandonment_parameter = \
            remaining_workload_ratio * (current_task.importance / 3)
        self.x20_abandonment_penalty=self.x20_abandonment_penalty+abandonment_parameter

        flag = False
        if player in self.players_handling_with_the_mission_previous:
            self.x3_abandonment_counter = self.x3_abandonment_counter + 1
            self.players_handling_with_the_mission_previous.remove(player)
            flag = True
        if flag and len(self.players_handling_with_the_mission_previous) == 0:
            self.x4_total_abandonment_counter = self.x4_total_abandonment_counter + 1

    def create_dict_of_players_amounts(self):
        ans = {}
        for i in range(self.max_players + 1):
            ans[i] = 0
        return ans

    def check_and_update_first_player_present(self, tnow):
        if self.x1_simulation_time_first_player_arrive is None:
            self.x1_simulation_time_first_player_arrive = copy.copy(tnow)
            self.x2_delay = tnow - self.x0_simulation_time_mission_enter_system

    def update_in_allocated_and_handled_before_delete(self, players_allocated_to_the_mission,
                                                      players_handling_with_the_mission):
        for pp in players_allocated_to_the_mission:
            self.players_allocated_to_the_mission_previous.append(pp)
        for ppp in players_handling_with_the_mission:
            self.players_handling_with_the_mission_previous.append(ppp)

    def update_mission_finished_workload(self, tnow):
        self.x5_simulation_time_mission_end = copy.copy(tnow)
        self.x6_total_time_since_arrive_to_system = copy.copy(tnow) - self.x0_simulation_time_mission_enter_system
        self.x7_total_time_since_first_agent_arrive = copy.copy(tnow) - self.x1_simulation_time_first_player_arrive
        self.x9_ratio_time_taken_arrive_to_system_and_opt = self.x8_optimal_time / self.x6_total_time_since_arrive_to_system
        self.x10_ratio_time_taken_first_agent_arrive_and_opt = self.x8_optimal_time / self.x7_total_time_since_first_agent_arrive

        self.calculate_mission_utility()

    def calculate_mission_utility(self):
        utility_per_workload = self.task_importance / self.initial_workload

        self.x16_workload_utility_without_zero = 0
        self.x17_workload_utility_with_zero =0
        for amount in self.x12_workload_per_quantity_time_in_system.keys():
            workload_in_system = self.x12_workload_per_quantity_time_in_system[amount]
            workload_in_system_with = self.x11_time_per_quantity_time_in_system[amount]

            self.x16_workload_utility_without_zero = self.x16_workload_utility_without_zero + utility_per_workload * workload_in_system * (
                        amount / self.max_players)
            self.x17_workload_utility_with_zero = self.x17_workload_utility_with_zero + utility_per_workload * workload_in_system_with * (
                        amount / self.max_players)

    def update_time_per_amount(self, current_amount_of_players, delta, productivity):


        current_time_per_quantity = self.x11_time_per_quantity_time_in_system[current_amount_of_players]
        current_workload_per_quantity = self.x12_workload_per_quantity_time_in_system[current_amount_of_players]

        self.x11_time_per_quantity_time_in_system[current_amount_of_players] = current_time_per_quantity + delta
        self.x12_workload_per_quantity_time_in_system[
            current_amount_of_players] = current_workload_per_quantity + delta * productivity


        if self.x1_simulation_time_first_player_arrive is not None:
            self.x13_time_per_quantity_time_first_player[current_amount_of_players] = current_time_per_quantity + delta
            self.x14_workload_per_quantity_time_first_player[
                current_amount_of_players] = current_workload_per_quantity + delta * productivity


class MissionSimple:
    """
    Class that represents a simple mission (as a part of the task)
    """

    def __init__(self, task_id,mission_id, initial_workload, arrival_time_to_the_system, task_importance = 1,
                 abilities=[AbilitySimple(ability_type=0)],
                 min_players=1, max_players=1):
        """
        Simple mission constructor
        :param mission_id: Mission's id
        :type mission_id: str
        :param initial_workload: The required workload of the mission (in seconds)
        :type initial_workload: float
        :param arrival_time_to_the_system: The time that task (with the mission)  arrived
        :param abilities:
        :param min_players:
        :param max_players:
        """
        self.task_id = task_id
        self.task_importance = task_importance
        self.mission_id = mission_id
        self.abilities = abilities
        self.min_players = min_players
        self.max_players = max_players
        self.initial_workload = initial_workload
        self.remaining_workload = initial_workload
        self.players_allocated_to_the_mission = []
        self.players_handling_with_the_mission = []
        self.is_done = False
        self.arrival_time_to_the_system = arrival_time_to_the_system
        self.last_updated = arrival_time_to_the_system
        self.measurements = MissionMeasurements(task_id = task_id,task_importance=self.task_importance, mission_id=self.mission_id,
                                                arrival_time_to_the_system=self.arrival_time_to_the_system,
                                                initial_workload=self.initial_workload, max_players=self.max_players)
        #####----------

        # self.x0_simulation_time_mission_enter_system = self.arrival_time_to_the_system
        # self.x1_simulation_time_first_player_arrive = None  # update when mission finish
        # self.x2_delay = None
        #
        # self.x3_abandonment_counter = 0  # each decrease in players present
        # self.x4_total_abandonment_counter = 0  # decrease from 1 to 0
        #
        # self.x8_optimal_time = self.initial_workload / self.max_players
        # self.x9_ratio_time_taken_arrive_to_system_and_opt = None
        # self.x10_ratio_time_taken_first_agent_arrive_and_opt = None
        #
        # self.x13_time_amount_of_agents_from_system = self.create_dict_of_players_amounts()
        # self.x14_time_amount_of_agents_and_time_mission_finish_ratio_system = self.create_dict_of_players_amounts()

    def create_dict_of_players_amounts(self):
        ans = {}
        for i in range(self.max_players + 1):
            ans[i] = None
        return ans

    def update_workload(self, tnow):
        delta = tnow - self.last_updated
        self.workload_updating(delta)
        if self.remaining_workload < 0.0001:
            self.is_done = True
            self.measurements.update_mission_finished_workload(tnow)
        self.last_updated = tnow

    def workload_updating(self, delta):
        productivity = 0
        counter = 0
        for p in self.players_handling_with_the_mission:
            counter = counter + 1
            if counter <= self.max_players:
                productivity += p.productivity
        self.remaining_workload -= delta * productivity
        current_amount_of_players = len(self.players_handling_with_the_mission)
        if counter <= self.max_players:
            self.measurements.update_time_per_amount(current_amount_of_players, delta, productivity)
        else:
            self.measurements.update_time_per_amount(self.max_players, delta, productivity)

        if self.remaining_workload < -0.01:
            raise Exception("Negative workload to mission" + str(self.mission_id))
        if len(self.players_handling_with_the_mission) > self.max_players:
            pass
            # raise Exception("Too many players allocated" + str(self.mission_id))

    def close_measurements(self):
        self.measurements.close_measurements()

    def add_allocated_player(self, player):
        if player in self.players_allocated_to_the_mission :
            print("Double allocation of the same player to one mission: player " + str(player.id_))
            #raise Exception("Double allocation of the same player to one mission: player " + str(player.id_))
        else:
            self.players_allocated_to_the_mission.append(player)

    def add_handling_player(self, player, tnow):
        if player in self.players_handling_with_the_mission:
            print("Double handling of the the same player to one mission" + str(self.mission_id))
            raise Exception("Double handling of the the same player to one mission" + str(self.mission_id))
        else:
            self.players_handling_with_the_mission.append(player)
            self.measurements.check_and_update_first_player_present(tnow)

    def remove_allocated_player(self, player):
        if player not in self.players_allocated_to_the_mission:
            raise Exception("Allocated player is not exist in the mission" + str(self.mission_id))
        self.players_allocated_to_the_mission.remove(player)

    def remove_handling_player(self, player):
        if player.status == Status.ON_MISSION:
            if player not in self.players_handling_with_the_mission:
                raise Exception("Allocated player is not exist in the mission")
            self.players_handling_with_the_mission.remove(player)
        self.remove_allocated_player(player)

    def clear_players_before_allocation(self):
        self.measurements.update_in_allocated_and_handled_before_delete(self.players_allocated_to_the_mission,
                                                                        self.players_handling_with_the_mission)

        self.players_allocated_to_the_mission.clear()
        self.players_handling_with_the_mission.clear()

    def change_abandonment_measurements(self, player,current_task,current_mission):
        self.measurements.change_abandonment_measurements(player=player,current_task = current_task,current_mission=current_mission)

    def __hash__(self):
        return hash(self.mission_id)

    def __eq__(self, other):
        return self.mission_id == other.mission_id

    def __str__(self):
        return str(self.mission_id)


class TaskSimple(Entity):
    """
    Class that represents a simple task in the simulation
    """

    def __init__(self, id_, location, importance, missions_list: list, arrival_time=0):
        """
        :param id_: The id of the task
        :type  id_: str
        :param location: The location of the task
        :type location: list of float
        :param importance: The importance of the task
        :type importance: int
        :param missions_list: the missions of the
        :param type_: The type of the task
        :type type_: int
        :param player_responsible, simulation will assign a responsible player to perform that algorithmic task
        computation and message delivery
        """
        Entity.__init__(self, id_, location, arrival_time)
        self.missions_list = missions_list
        self.player_responsible = None
        self.importance = importance
        self.arrival_time = arrival_time  # arrival time to system
        self.done_missions = []
        self.is_done = False

    def create_neighbours_list(self, players_list,
                               f_is_player_can_be_allocated_to_mission=is_player_can_be_allocated_to_task):
        """
        Creates
        :param players_list:
        :param f_is_player_can_be_allocated_to_mission:
        :return:
        """
        for a in players_list:
            self.neighbours.append(a.id_)

    def update_workload_for_missions(self, tnow):

        for m in self.missions_list:
            m.update_workload(tnow)
        self.update_time(tnow)

    def mission_finished(self, mission):

        mission.is_done = True

        self.missions_list.remove(mission)
        self.done_missions.append(mission)


        if len(self.missions_list) == 0:
            self.is_done = True


def amount_of_task_responsible(player):
    return len(player.tasks_responsible)

def find_and_allocate_responsible_player(task: TaskSimple, players):
    distances = []
    for player in players:
        # for mission in task.missions_list:
        #     for ability in mission.abilities:
        #         if ability in player.abilities:
        distances.append(calculate_distance(task, player))

    min_distance = min(distances)

    players_min_distances = []

    for player in players:
        if calculate_distance(task, player) == min_distance:
             #for mission in task.missions_list:
             #    for ability in mission.abilities:
             #        if ability in player.abilities:
            players_min_distances.append(player)

    selected_player = min(players_min_distances, key=amount_of_task_responsible)
    selected_player.tasks_responsible.append(task)
    task.player_responsible = selected_player

if __name__ == '__main__':
    stg = SimpleTaskGenerator(max_number_of_missions = 3 ,map_= MapSimple(), seed=1, max_importance=10)
    task_list = stg.get_tasks_number_of_tasks_now(0,10)