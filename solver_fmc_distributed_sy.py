from simulation_abstract_components import TaskSimple, PlayerSimple
from solver_abstract import default_communication_disturbance, AllocationSolverSingleTaskInit, \
    AllocationSolverAllPlayersInit, Msg
from solver_fmc_distributed_asy import FisherTaskASY, is_with_scheduling, FisherTaskASY_greedy_Schedual, \
    FisherPlayerASY_greedy_Schedual

debug_sy = False

class FisherTaskSY_greedy_Schedual(FisherTaskASY_greedy_Schedual):
    def __init__(self, agent_simulator: TaskSimple, t_now, is_with_timestamp, counter_of_converges=4, Threshold=0.001):

        FisherTaskASY_greedy_Schedual.__init__(self, agent_simulator=agent_simulator, t_now=t_now, is_with_timestamp=is_with_timestamp,
                               counter_of_converges=counter_of_converges, Threshold=Threshold)
        self.msgs_timestamp = {}
        self.reset_msgs_timestamp()


    def more_reset_additional_fields(self):
        FisherTaskASY_greedy_Schedual.more_reset_additional_fields(self)
        self.reset_msgs_timestamp()

    def reset_msgs_timestamp(self):
        self.msgs_timestamp = {}
        for player_id in self.potential_players_ids_list:
            self.msgs_timestamp[player_id] = 0

    def update_msgs_timestamp_dict(self,msg):
        if debug_sy:

            if self.simulation_entity.id_ == "3" and self.timestamp_counter == 12:
                print(msg.sender)
        sender_id = msg.sender
        timestamp_msg = msg.timestamp
        self.msgs_timestamp[sender_id] = timestamp_msg

    def set_receive_flag_to_true_given_msg(self, msg):
        self.update_msgs_timestamp_dict(msg)
        for timestamp_in_memory in self.msgs_timestamp.values():
            if timestamp_in_memory - 1 != self.timestamp_counter:
                return
        self.calculate_xjk_flag = True

    def get_list_of_msgs_to_send(self):
        ans = []
        for n_id in self.potential_players_ids_list:
            xij_market = {}
            xij_normal = {}
            for mission in self.simulation_entity.missions_list:
                x_ijk = self.x_jk[mission][n_id]
                xij_normal_val = self.x_jk_normal[mission][n_id]

                xij_market[mission] = x_ijk
                xij_normal[mission] = xij_normal_val

            information_to_send = [xij_market, xij_normal]
            addition_to_info = self.list_of_info_to_send_beside_allocation(n_id)
            if addition_to_info is not None:
                information_to_send = information_to_send + addition_to_info

            is_perfect_com = False
            if self.simulation_entity.player_responsible is not None:

                if self.simulation_entity.player_responsible.id_ == n_id:
                    is_perfect_com = True
            msg = Msg(sender=self.simulation_entity.id_, receiver=n_id, information=information_to_send,
                      is_with_perfect_communication=is_perfect_com)
            ans.append(msg)
        return ans




class FisherPlayerSY_greedy_Schedual(FisherPlayerASY_greedy_Schedual):
    def __init__(self, util_structure_level, agent_simulator, t_now, future_utility_function, is_with_timestamp, ro=0.9,tasks_ids = []):
        FisherPlayerASY_greedy_Schedual.__init__(self ,util_structure_level = util_structure_level, agent_simulator=agent_simulator,
                                 t_now=t_now, future_utility_function=future_utility_function,
                                 is_with_timestamp=is_with_timestamp, ro=ro)

        self.tasks_ids = tasks_ids
        self.msgs_timestamp = {}
        self.reset_msgs_timestamp()

    def reset_msgs_timestamp(self):
        self.msgs_timestamp = {}
        for task_id in self.tasks_ids:
            self.msgs_timestamp[task_id] = -1

    def more_reset_additional_fields(self):


        FisherPlayerASY_greedy_Schedual.more_reset_additional_fields(self)
        self.reset_msgs_timestamp()

    def update_msgs_timestamp_dict(self,msg):
        if debug_sy:
            pass
            #if self.simulation_entity.id_ == -9 and self.timestamp_counter == 13:
            #    print(msg.sender)
        sender_id = msg.sender
        timestamp_msg = msg.timestamp
        self.msgs_timestamp[sender_id] = timestamp_msg

    def set_receive_flag_to_true_given_msg(self, msg):
        self.update_msgs_timestamp_dict(msg)
        for timestamp_in_memory in self.msgs_timestamp.values():
            if timestamp_in_memory  != self.timestamp_counter:
                return
        self.calculate_bids_flag = True


class FMC_TA(AllocationSolverAllPlayersInit):
    def __init__(self, util_structure_level=1, mailer=None, f_termination_condition=None, f_global_measurements={},
                 f_communication_disturbance=default_communication_disturbance, future_utility_function=None,
                 is_with_timestamp=True, ro=0.9, counter_of_converges=3, Threshold=10 ** -5):
        AllocationSolverAllPlayersInit.__init__(self, mailer, f_termination_condition,
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

        tasks_ids = []
        for task in self.tasks_simulation:
            tasks_ids.append(task.id_)

        return FisherPlayerSY_greedy_Schedual(util_structure_level=self.util_structure_level,
                                               agent_simulator=player, t_now=self.tnow,
                                               future_utility_function=self.future_utility_function,
                                               is_with_timestamp=self.is_with_timestamp, ro=self.ro,tasks_ids = tasks_ids)

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