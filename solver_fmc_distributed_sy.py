from simulation_abstract_components import TaskSimple, PlayerSimple
from solver_abstract import default_communication_disturbance, AllocationSolverSingleTaskInit, \
    AllocationSolverAllTasksInit, Msg
from solver_fmc_distributed_asy import FisherTaskASY, is_with_scheduling, FisherTaskASY_greedy_Schedual, \
    FisherPlayerASY_greedy_Schedual


class FisherTaskSY_greedy_Schedual(FisherTaskASY_greedy_Schedual):
    def __init__(self, agent_simulator: TaskSimple, t_now, is_with_timestamp, counter_of_converges=4, Threshold=0.001):

        FisherTaskASY.__init__(self, agent_simulator=agent_simulator, t_now=t_now, is_with_timestamp=is_with_timestamp,
                               counter_of_converges=counter_of_converges, Threshold=Threshold)
        self.max_time_per_mission = {}
        self.player_greedy_arrive_dict = {}
        self.reset_mission_per_allocation_list()

    def set_receive_flag_to_true_given_msg_after_check(self, msg):
        if self.msgs_time_stamp_one_more_then_to_me():
            self.calculate_xjk_flag = True
            # TODO

    def msgs_time_stamp_one_more_then_to_me(self):

        for msg in self.msgs_from_players.values():
            if msg == None:
                return False
            if msg.timestamp - 1 != self.timestamp_counter:
                return False
        print(self.simulation_entity.id_)

        return True

    def set_receive_flag_to_true_given_msg(self, msg: Msg):
        self.set_receive_flag_to_true_given_msg_after_check(msg)

    def reset_mission_per_allocation_list(self):
        for mission in self.simulation_entity.missions_list:
            self.player_greedy_arrive_dict[mission] = {}
            self.max_time_per_mission[mission] = None

    def more_reset_additional_fields(self):

        self.reset_mission_per_allocation_list()

    def update_more_information_index_2_and_above(self, player_id, msg):
        if is_with_scheduling:
            if len(self.player_greedy_arrive_dict) == 0:
                self.reset_mission_per_allocation_list()
            allocations_dict = msg.information[2]
            player_id_sender = msg.sender
            for mission, time_arrive in allocations_dict.items():
                try:
                    self.player_greedy_arrive_dict[mission][player_id_sender] = time_arrive
                except:
                    print("line 1050")
        else:
            pass

    def compute_schedule(self):
        if is_with_scheduling:
            self.compute_max_time_per_mission()
        else:
            pass

    def compute_max_time_per_mission(self):
        for mission in self.simulation_entity.missions_list:
            arrives_per_mission = []
            arrive_time_dict = self.player_greedy_arrive_dict[mission]
            for time_ in arrive_time_dict.values():
                if time_ is not None:
                    arrives_per_mission.append(time_)
            if len(arrives_per_mission) == 0:
                self.max_time_per_mission[mission] = None
            else:
                self.max_time_per_mission[mission] = max(arrives_per_mission)

    def list_of_info_to_send_beside_allocation(self, player_id: str) -> []:
        if is_with_scheduling:
            return [self.max_time_per_mission]
        else:
            pass



class FisherPlayerSY_greedy_Schedual(FisherPlayerASY_greedy_Schedual):
    def __init__(self, util_structure_level, agent_simulator, t_now, future_utility_function, is_with_timestamp, ro=0.9):
        FisherPlayerASY_greedy_Schedual.__init__(self ,util_structure_level = util_structure_level, agent_simulator=agent_simulator,
                                 t_now=t_now, future_utility_function=future_utility_function,
                                 is_with_timestamp=is_with_timestamp, ro=ro)

    def set_receive_flag_to_true_given_msg_after_check(self, msg):
        if self.msgs_time_stamp_equals_to_me():
            self.calculate_bids_flag = True


    def msgs_time_stamp_equals_to_me(self):
        for task in self.tasks_log:
            if task.id_ not in self.msgs_from_tasks.keys():
                return False

        for task in self.tasks_log:
            msg = self.msgs_from_tasks[task.id_]

            if msg.timestamp != self.timestamp_counter:
                return False
        print(self.simulation_entity.id_)
        return True


    def set_receive_flag_to_true_given_msg(self, msg: Msg):
        self.set_receive_flag_to_true_given_msg_after_check(msg)

class FMC_TA(AllocationSolverAllTasksInit):
    def __init__(self, util_structure_level=1, mailer=None, f_termination_condition=None, f_global_measurements={},
                 f_communication_disturbance=default_communication_disturbance, future_utility_function=None,
                 is_with_timestamp=True, ro=0.9, counter_of_converges=3, Threshold=10 ** -5):
        AllocationSolverSingleTaskInit.__init__(self, mailer, f_termination_condition,
                                                f_global_measurements,
                                                f_communication_disturbance)
        self.util_structure_level = util_structure_level
        self.ro = ro
        self.future_utility_function = future_utility_function
        self.is_with_timestamp = is_with_timestamp
        self.counter_of_converges = counter_of_converges
        self.Threshold = Threshold

    def __str__(self):
        return "FMC_TA"

    def create_algorithm_task(self, task: TaskSimple):
        return FisherTaskSY_greedy_Schedual(agent_simulator=task, t_now=self.tnow,
                                             is_with_timestamp=self.is_with_timestamp,
                                             counter_of_converges=self.counter_of_converges, Threshold=self.Threshold)

    def create_algorithm_player(self, player: PlayerSimple):
        return FisherPlayerSY_greedy_Schedual(util_structure_level=self.util_structure_level,
                                               agent_simulator=player, t_now=self.tnow,
                                               future_utility_function=self.future_utility_function,
                                               is_with_timestamp=self.is_with_timestamp, ro=self.ro)

    def allocate(self):
        self.reset_algorithm_agents()
        self.mailer.reset(self.tnow)
        # should_allocate = self.solve_tasks_with_players_that_pay_them_all_bug()
        self.connect_entities()
        self.agents_initialize()
        self.start_all_threads()
        self.mailer.start()
        self.mailer.join()
        return self.mailer.time_mailer.clock