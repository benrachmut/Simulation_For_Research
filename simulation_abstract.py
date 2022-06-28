import random
from abc import ABC
from itertools import filterfalse

from simulation_abstract_components import TaskGenerator, TaskSimple, calculate_distance, \
    find_and_allocate_responsible_player, PlayerSimple, MissionSimple, Status, Entity


class SimulationEvent:
    """
    Class that represents an event in the simulation log.
    """

    def __init__(self, time_, player=None, task=None, mission=None):
        """
        :param time_:the time of the event
        :type: float
        :param player: The relevant player for this simulation event. Can be None(depends on extension).
        :type: PlayerSimple
        :param task: The relevant task(task) to this simulation event. Can be None(depends on extension).
        :type: TaskSimple
        :param mission: The relevant mission (of task) for this simulation event. Can be None(depends on extension).
        :type: MissionSimple

        """
        self.time = time_
        self.player = player
        self.mission = mission
        self.task = task

    def __hash__(self):
        return hash(self.time)

    def __lt__(self, other):
        return self.time < other.time

    def handle_event(self, simulation):
        """
        Handle with the task when it arrives in the simulation
        :param simulation: the simulation where the the task appears
        :type: Simulation
        :return:
        """
        raise NotImplementedError

    def __str__(self):
        return "time:" + str(self.time) + "\tevent type:" + str(type(self)) + "\tplayer:" + str(
            self.player) + "\ttask:" + str(
            self.task) + "\tmission:" + str(self.mission)


class EndSimulationEvent(SimulationEvent):
    def handle_event(self, simulation):
        pass

    def __init__(self, time_: float):
        """
        :param time_:the time of the event (Simulation completion time)
        :type: float
        """
        SimulationEvent.__init__(self, time_=time_)


class TaskArrivalEvent(SimulationEvent):
    """
    Class that represent a simulation event of new task arrival.
    """

    def __init__(self, time_: float, task: TaskSimple):
        """
        :param time_:the time of the event
        :type: float
        :param task: The new task that arrives to simulation.
        :type: TaskSimple
        """
        SimulationEvent.__init__(self, time_=time_, task=task)

    def handle_event(self, simulation):
        find_and_allocate_responsible_player(task=self.task, players=simulation.players_list)
        simulation.tasks_list.append(self.task)
        simulation.solver.add_task_to_solver(self.task)
        simulation.remove_solver_finish_event()
        simulation.solve()
        simulation.generate_new_task_to_diary()


class TaskArrivalToMainComputerEvent(SimulationEvent):
    """
    Class that represent a simulation event of new task arrival.
    """

    def __init__(self, time_: float, task: TaskSimple):
        """
        :param time_:the time of the event
        :type: float
        :param task: The new task that arrives to simulation.
        :type: TaskSimple
        """
        SimulationEvent.__init__(self, time_=time_, task=task)

    def handle_event(self, simulation):
        find_and_allocate_responsible_player(task=self.task, players=simulation.players_list)

        simulation.tasks_list.append(self.task)
        simulation.solver.add_task_to_solver(self.task)
        simulation.remove_solver_finish_event()

        simulation.solve()

class NumberOfTasksArrivalEvent(SimulationEvent):
    """
    Class that represent an simulation event of new tasks arrival.
    """

    def __init__(self, is_static, time_: float, tasks: [TaskSimple], task=None, ):
        """
        :param time_:the time of the event
        :type: float
        :param task: The new task that arrives to simulation.
        :type: TaskSimple
        """
        SimulationEvent.__init__(self, time_=time_, task=task)
        self.tasks = tasks
        self.is_static = is_static

    def handle_event(self, simulation):
        for task in self.tasks:
            find_and_allocate_responsible_player(task=task, players=simulation.players_list)
            simulation.tasks_list.append(task)
            simulation.solver.add_task_to_solver(task)

        simulation.solve()

        if not self.is_static:
            simulation.generate_new_task_to_diary()


class SolverFinishEvent(SimulationEvent):
    def __init__(self, time_):
        """
        :param time:the time of the event
        :type: float
        :param player: The relevant player that arrives to the given mission on the given task.
        :type: PlayerSimple
        :param task: The relevant task that contain the given mission
        :type: TaskSimple
        :param mission: The mission that the player arrives to.
        :type: MissionSimple
        """
        SimulationEvent.__init__(self, time_=time_)

    def handle_event(self, simulation):
        simulation.remove_mission_finished_events()
        simulation.remove_player_arrive_to_mission_event_from_diary()
        simulation.clear_players_before_allocation()
        simulation.check_new_allocation()


class TaskFinishedEvent(SimulationEvent):
    """
    Class that represent an event of player finished to handle  with the mission.
    """

    def __init__(self, time_, task, mission):
        """
        :param time_:the time of the event
        :type: float
        :param player: The relevant player that arrives to the given mission on the given task.
        :type: PlayerSimple
        :param task: The relevant task that contain the given mission
        :type: TaskSimple
        :param mission: The mission that the player arrives to.
        :type: MissionSimple
        """
        SimulationEvent.__init__(self, time_=time_, task=task, mission=mission)

    def handle_event(self, simulation):
        for player in self.mission.players_allocated_to_the_mission:
            simulation.remove_events_when_mission_finished(self.mission)
            player.schedule[:] = filterfalse(lambda a: a[1].is_done, player.schedule)
            if len(player.schedule) >= 1:
                simulation.generate_player_arrives_to_mission_event(player=player)
            else:
                player.update_status(Status.IDLE, self.time)
                player.current_mission = None
                player.current_task = None
                # simulation.generate_player_update_event(player=player)

        self.mission.players_allocated_to_the_mission = []
        self.mission.players_handling_with_the_mission = []
        self.task.mission_finished(self.mission)
        if self.task.is_done:
            simulation.handle_task_ended(self.task)
            simulation.solver.remove_task_from_solver(self.task)
        # simulation.generate_task_update_event(task=self.task)


class PlayerArriveToTaskEvent(SimulationEvent):
    """
    Class that represent an event of player's arrival to the mission.
    """

    def __init__(self, time_, player, task, mission):
        """
        :param time_:the time of the event
        :type: float
        :param player: The relevant player that arrives to the given mission on the given task.
        :type: PlayerSimple
        :param task: The relevant task that contain the given mission
        :type: TaskSimple
        :param mission: The mission that the player arrives to.
        :type: MissionSimple
        """
        SimulationEvent.__init__(self, time_=time_, task=task, mission=mission, player=player)

    def handle_event(self, simulation):
        self.player.update_location(self.task.location, self.time)
        self.player.update_status(Status.ON_MISSION, self.time)
        if len(self.player.schedule) > 0 and self.player.current_task.id_ == self.player.schedule[0][0].id_:
            self.player.schedule.pop(0)
        self.mission.add_handling_player(self.player, self.time)
        self.task.update_arrive_time(self.time)

        simulation.generate_mission_finished_event(mission=self.mission, task=self.task)
        # simulation.generate_player_update_event(player=self.player)
        # simulation.generate_task_update_event(task=self.task)


class PlayerReceivesNewAllocation(SimulationEvent, ABC):

    def __init__(self, time_, player):
        """
        :param time_:the time of the event
        :type: float
        :param player: The relevant player that arrives to the given mission on the given task.
        :type: PlayerSimple
        """
        SimulationEvent.__init__(self, time_=time_, player=player)

    def handle_event(self, simulation):
        simulation.check_new_allocation_for_player(self.player)




class newTaskDiscoveredEvent(SimulationEvent):
    """
    Class that represent a simulation event of message arrival to main computer, about discovered new event
    """

    def __init__(self, time_: float, task: TaskSimple):
        """
        :param time_:the time of the event
        :type: float
        :param task: The new task that arrives to simulation.
        :type: TaskSimple
        """
        SimulationEvent.__init__(self, time_=time_, task=task)

    def handle_event(self, simulation):
        find_and_allocate_responsible_player(task=self.task, players=simulation.players_list)
        delay = simulation.f_generate_message_disturbance(simulation.main_computer_entity, self.task)  # # TODO BEN
        if delay is None:
            simulation.generate_new_task_to_diary()
            return
        ev = TaskArrivalToMainComputerEvent(task=self.task, time_=self.time + delay)
        simulation.diary.append(ev)
        simulation.generate_new_task_to_diary()  # Ask Ben?


class CentralizedSolverFinishEvent(SimulationEvent):
    def __init__(self, time_):
        """
        :param time:the time of the event
        :type: float
        :param player: The relevant player that arrives to the given mission on the given task.
        :type: PlayerSimple
        :param task: The relevant task that contain the given mission
        :type: TaskSimple
        :param mission: The mission that the player arrives to.
        :type: MissionSimple
        """
        SimulationEvent.__init__(self, time_=time_)

    def handle_event(self, simulation):
        simulation.generate_players_receive_allocation_events()


def get_mission_from_task_by_id(next_task, mission_id):
    for mission in next_task.missions_list:
        if mission.mission_id == mission_id:
            return mission


def default_communication_disturbance():
    return False


class SimulationV1:
    def __init__(self, name: str, players_list: list, solver, tasks_generator: TaskGenerator, end_time: float,
                 number_of_initial_tasks=10, is_static=True, debug_mode_full=False,debug_mode_light = True
                 ):
        """
        :param name: The name of simulation
        :param players_list: The list of the players(players) that are participate
        :param solver: The algorithm that solve the task allocation problem
        :param tasks_generator: Task generator
        :param end_time: Simulation completion time
        :param f_are_players_neighbours: functions that checks if the players are player
        :param f_is_player_can_be_allocated_to_task: The function checks if the player can be allocated to mission
        :param f_calculate_distance: calculate the distance
        """
        # self.f_generate_message_disturbance = f_generate_message_disturbance

        self.is_static = is_static
        self.tnow = 0
        self.prev_time = 0
        self.last_event = None
        self.name = name
        self.diary = []
        # players initialization
        self.players_list = players_list
        # solver initialization
        self.solver = solver
        self.solver.add_players_list(players_list)
        # tasks initialization
        self.tasks_generator = tasks_generator
        self.f_calculate_distance = calculate_distance
        self.generate_new_task_to_diary(number_of_tasks=number_of_initial_tasks)
        self.tasks_list = []
        self.finished_tasks_list = []
        self.diary.append(EndSimulationEvent(time_=end_time))
        self.debug_mode_full = debug_mode_full
        self.debug_mode_light = debug_mode_light

        self.solver_counter = 0
        self.run_simulation()

    def run_simulation(self):
        while True:
            self.diary = sorted(self.diary, key=lambda event: event.time)
            self.last_event = self.diary.pop(0)
            if self.debug_mode_full:
                print(self.last_event)
            if type(self.last_event) == EndSimulationEvent:
                self.close_mission_measurements()
                break
            self.prev_time = self.tnow
            self.tnow = self.last_event.time
            self.update_workload()
            self.last_event.handle_event(self)

    def close_mission_measurements(self):
        for task in self.tasks_list:
            for mission in task.missions_list:
                mission.close_measurements()
                # done_missions
                task.done_missions.append(mission)
            task.missions_list.clear()
            self.finished_tasks_list.append(task)

    def solve(self):
        self.solver_counter = self.solver_counter + 1
        if self.debug_mode_full or self.debug_mode_light:
            print("SOLVER STARTS:", self.solver_counter)
        self.update_locations_of_players()
        solver_duration_NCLO = self.solver.solve(self.tnow)
        if self.debug_mode_full or self.debug_mode_light:
            print("SOLVER finish with time:", solver_duration_NCLO)
        time = self.tnow
        if self.is_static == False:
            time = self.tnow + solver_duration_NCLO
            if self.check_diary_during_solver(time):
                self.update_workload()
                self.diary.append(SolverFinishEvent(time_=time))
                return
            self.tnow = time
            self.update_workload()
        else:
            self.tnow = time

        # handle_new allocation

        self.remove_mission_finished_events()
        self.remove_player_arrive_to_mission_event_from_diary()
        self.clear_players_before_allocation()
        self.check_new_allocation()
        # print(self.diary)

    def check_new_allocation(self):
        # if not self.is_centralized:
        for player in self.players_list:
            self.check_new_allocation_for_player(player)
        # else:
        # for player in self.players_list:
        # self.generate_update_player_event(player)

    def check_new_allocation_for_player(self, player):
        self.clean_schedule(player)
        if player.current_mission is None:  # The agent doesn't have a current mission
            if len(player.schedule) == 0:  # The agent doesn't have a new allocation
                player.update_status(Status.IDLE, self.tnow)
            else:  # The agent has a new allocation
                self.generate_player_arrives_to_mission_event(player=player)
        else:  # The player has a current allocation
            if len(player.schedule) == 0:  # Player doesn't have a new allocation (only the old one)
                self.handle_abandonment_event(player=player, mission=player.current_mission,
                                              task=player.current_task)
                player.update_status(Status.IDLE, self.tnow)
            else:  # The player has a new allocation (missions in schedule)
                if player.schedule[0][1] == player.current_mission:  # The players remains in his current mission
                    if player.status == Status.ON_MISSION:  # If the has already arrived to the mission
                        player.current_mission.add_allocated_player(player)
                        player.current_mission.add_handling_player(player, self.tnow)
                        player.current_task.update_arrive_time(self.tnow)

                        self.generate_mission_finished_event(mission=player.current_mission,
                                                             task=player.current_task)
                        player.schedule.pop(0)
                    elif player.status == Status.TO_MISSION:
                        self.generate_player_arrives_to_mission_event(player=player)
                else:  # The player abandons his current event to a new allocation
                    self.handle_abandonment_event(player=player, mission=player.current_mission,
                                                  task=player.current_task)
                    self.generate_player_arrives_to_mission_event(player=player)
                    # self.generate_player_arrives_to_mission_event(player=player)

    def update_workload(self):
        for t in self.tasks_list:
            t.update_workload_for_missions(self.tnow)

    def update_locations_of_players(self):
        for player in self.players_list:
            player.calculate_relative_location(self.tnow)

    def handle_abandonment_event(self, player: PlayerSimple, mission: MissionSimple, task: TaskSimple):
        mission.change_abandonment_measurements(player=player, current_mission=mission, current_task=task)
        player.current_mission = None
        player.current_task = None
        self.generate_mission_finished_event(mission, task)
        # self.generate_task_update_event(task=task)

    def handle_task_ended(self, task):
        self.finished_tasks_list.append(task)
        self.tasks_list.remove(task)

    def remove_mission_finished_events(self):
        self.diary[:] = filterfalse(lambda ev: type(ev) == TaskFinishedEvent, self.diary)

    def remove_mission_finished_event(self, mission: MissionSimple):
        self.diary[:] = filterfalse(
            lambda ev: type(ev) == TaskFinishedEvent and ev.mission.mission_id == mission.mission_id, self.diary)

    def remove_player_arrive_to_mission_event_from_diary(self):
        self.diary[:] = filterfalse(lambda ev: type(ev) == PlayerArriveToTaskEvent, self.diary)

    def remove_solver_finish_event(self):
        self.diary[:] = filterfalse(lambda ev: type(ev) == SolverFinishEvent, self.diary)

    def remove_events_when_mission_finished(self, mission: MissionSimple):
        self.diary[:] = filterfalse(lambda ev: ev.mission is not None and ev.mission.mission_id == mission.mission_id,
                                    self.diary)

    def clear_players_before_allocation(self):
        for t in self.tasks_list:
            for m in t.missions_list:
                m.clear_players_before_allocation()

    def generate_new_task_to_diary(self, number_of_tasks=1):
        """
        The method generates new task from task generator, creates neighbour list for the task and add TaskArrivalEvent
        to the diary.
        """
        if number_of_tasks == 1:
            task: TaskSimple = self.tasks_generator.get_task(self.tnow)
            if task is not None:
                task.create_neighbours_list(players_list=self.players_list)
                event = TaskArrivalEvent(task=task, time_=task.arrival_time)
                self.diary.append(event)
        else:
            tasks = self.tasks_generator.get_tasks_number_of_tasks_now(self.tnow, number_of_tasks)
            event = NumberOfTasksArrivalEvent(is_static=self.is_static, tasks=tasks, time_=tasks[0].arrival_time)
            self.diary.append(event)

    def get_simulation_task_by_id(self, task_id):
        for task_sim in self.tasks_list:
            if task_sim.id_ == task_id:
                return task_sim

    def generate_player_arrives_to_mission_event(self, player):
        player.update_status(Status.TO_MISSION, self.tnow)
        task_id = player.schedule[0][0].id_
        next_task = self.get_simulation_task_by_id(task_id)
        if next_task is not None:
            mission_id = player.schedule[0][1].mission_id

            # next_mission = get_mission_from_task_by_id(next_task, mission_id)
            # if next_mission is None:
            #
            #     print("aaaaaaaa")

            next_mission = get_mission_from_task_by_id(next_task, mission_id)
            next_mission.add_allocated_player(player)
            player.current_mission = next_mission
            player.current_task = next_task
            travel_time = self.f_calculate_distance(player, next_task) / player.speed
            # self.generate_player_update_event(player=player)

            self.diary.append(
                PlayerArriveToTaskEvent(time_=self.tnow + travel_time, task=next_task, mission=next_mission,
                                        player=player))
        else:
            player.update_status(Status.IDLE, self.tnow)

    def generate_mission_finished_event(self, mission, task):
        """
        Removes task finished event
        :param mission:
        :param task:
        :return:
        """
        self.remove_mission_finished_event(mission=mission)
        sum_productivity = 0
        if len(mission.players_handling_with_the_mission) == 0:
            return
        for p in mission.players_handling_with_the_mission:
            sum_productivity += p.productivity
        duration = mission.remaining_workload / sum_productivity
        mission_finish_simulation_time = self.tnow + duration
        self.diary.append(
            TaskFinishedEvent(time_=mission_finish_simulation_time, mission=mission, task=task))

    def check_diary_during_solver(self, time):
        self.diary = sorted(self.diary, key=lambda event_: event_.time)
        for event in self.diary:
            if event.time > time:
                return False
            else:
                return True

    def get_player_from_simulation_by_id_from_central_computer(self, player_id_):
        for p in self.solver.centralized_computer.players_simulation:
            if p.id_ == player_id_:
                return p

    def clean_schedule(self, player):
        count = 0
        for all in player.schedule:
            task_id = all[0].id_
            next_task = self.get_simulation_task_by_id(task_id)
            if next_task is None:
                count += 1
                continue
            mission_id = all[1].mission_id
            next_mission = get_mission_from_task_by_id(next_task, mission_id)
            if next_mission is None:
                count += 1
                continue
            break
        for _ in range(count):
            player.schedule.pop(0)


class SimulationV2(SimulationV1):

    def __init__(self, name: str, players_list: list, solver, f_generate_message_disturbance,
                 tasks_generator: TaskGenerator, end_time: float,
                 number_of_initial_tasks=10,
                 is_static=True,
                 debug_mode_full=False,
                 debug_mode_light = True
                 ):
        """
        :param name: The name of simulation
        :param players_list: The list of the players(players) that are participate
        :param solver: The algorithm that solve the task allocation problem
        :param tasks_generator: Task generator
        :param end_time: Simulation completion time
        :param f_generate_message_disturbance:
        :param number_of_initial_tasks:
        :param is_static:
        :param debug_mode:
        """
        self.f_generate_message_disturbance = f_generate_message_disturbance
        self.main_computer_entity = Entity(id_="main computer", location=[0, 0])
        SimulationV1.__init__(self, name, players_list, solver, tasks_generator, end_time,
                              number_of_initial_tasks, is_static, debug_mode_full, debug_mode_light)

    def solve(self):
        self.solver_counter = self.solver_counter + 1
        if self.debug_mode_full or self.debug_mode_light:
            print("SOLVER STARTS:", self.solver_counter)
        solver_duration_NCLO = self.solver.solve(self.tnow)
        if self.debug_mode_full or self.debug_mode_light:
            print("SOLVER finish with time:", solver_duration_NCLO)
        time = self.tnow
        if not self.is_static:
            time = self.tnow + solver_duration_NCLO
            if self.check_diary_during_solver(time):
                #self.update_workload()
                self.diary.append(CentralizedSolverFinishEvent(time_=time))
                return
            self.tnow = time
            self.update_workload()
        else:
            self.tnow = time
        self.generate_players_receive_allocation_events()

    def generate_players_receive_allocation_events(self):
        for p in self.players_list:
            delay_time = self.f_generate_message_disturbance(self.main_computer_entity, p)  # TODO BEN
            if delay_time is None:
                continue
            e = PlayerReceivesNewAllocation(time_=self.tnow + delay_time, player=p)
            self.diary.append(e)

    def generate_new_task_to_diary(self, number_of_tasks=1):
        """
        The method generates new task from task generator, creates neighbour list for the task and
        add newTaskDiscoveredEvent to the diary.
        """
        if number_of_tasks == 1:
            task: TaskSimple = self.tasks_generator.get_task(self.tnow)
            if task is not None:
                task.create_neighbours_list(players_list=self.players_list)
                event = newTaskDiscoveredEvent(task=task, time_=task.arrival_time)
                self.diary.append(event)
        else:
            tasks = self.tasks_generator.get_tasks_number_of_tasks_now(self.tnow, number_of_tasks)
            event = NumberOfTasksArrivalEvent(is_static=self.is_static, tasks=tasks, time_=tasks[0].arrival_time)
            self.diary.append(event)

    def remove_player_arrive_to_mission_event_from_diary_before_agent_arrived(self, mission, player):
        self.diary[:] = filterfalse(lambda ev: type(ev) == PlayerArriveToTaskEvent and
                                               ev.mission.mission_id == mission.mission_id and
                                               ev.player.id_ == player.id_, self.diary)

    def check_new_allocation_for_player(self, player):
        self.clean_schedule(player=player)
        if player.current_mission is None:  # The agent doesn't have a current mission
            if len(player.schedule) == 0:  # The agent doesn't have a new allocation
                player.update_status(Status.IDLE, self.tnow)
            else:  # The agent has a new allocation
                self.generate_player_arrives_to_mission_event(player=player)

        else:  # The player has a current allocation
            if len(player.schedule) == 0:  # Player doesn't have a new allocation (only the old one)
                self.handle_abandonment_event(player=player, mission=player.current_mission,
                                              task=player.current_task)
                player.update_status(Status.IDLE, self.tnow)
            else:  # The player has a new allocation (missions in schedule)
                if player.schedule[0][1] == player.current_mission:  # The players remains in his current mission
                    if player.status == Status.ON_MISSION:  # If the has already arrived to the mission
                        player.schedule.pop(0)


                else:  # The player abandons his current event to a new allocation

                    if player.status == Status.ON_MISSION:
                        player.current_mission.remove_handling_player(player=player)
                    elif player.status == Status.TO_MISSION:
                        player.current_mission.remove_allocated_player(player=player)
                        self.remove_player_arrive_to_mission_event_from_diary_before_agent_arrived(
                            mission=player.current_mission, player=player)
                    self.handle_abandonment_event(player=player, mission=player.current_mission,
                                                  task=player.current_task)
                    self.generate_player_arrives_to_mission_event(player=player)
