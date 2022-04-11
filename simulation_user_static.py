import random

from general_communication_protocols import CommunicationProtocolLossExponent, CommunicationProtocolDelayExponent
from general_data_fisher_market import get_data_fisher
from general_r_ij import calculate_rij_abstract
from simulation_abstract import Simulation
from simulation_abstract_components import SimpleTaskGenerator, MapSimple, PlayerSimple, AbilitySimple
from solver_fmc import FMC_ATA, FisherTaskASY

is_static = True
start = 0
end = 2
size_players = 10
end_time = 10**8
size_of_initial_tasks = 10
max_nclo_algo_run = 10000

#--- 1 = DATA  ---
fisher_data_jumps = 100

##--- 1 = distributed FMC_ATA;  ---
solver_number = 1
counter_of_converges=2
Threshold=10**-5


# --- communication_protocols ---
std = 10
alphas_LossExponent = [0.1, 0.5, 1, 1.5, 2]
alphas_delays = [100,200,300,500]

##--- map ---
length = 900.0
width = 900.0

##--- task generator ---
max_number_of_missions = 3
max_importance = 10000

##--- agents ---
speed = 100


# name,alpha,delta_x,delta_y,



def f_termination_condition_all_tasks_converged(agents_algorithm, mailer):
    # TODO take care of only 1 task in system
    if mailer.time_mailer.get_clock() > max_nclo_algo_run:
        return True

    tasks = []
    players = []
    for agent in agents_algorithm:
        if isinstance(agent,FisherTaskASY):
            tasks.append(agent)
        else:
            players.append(agent)

    for task in tasks:
        if not task.is_finish_phase_II and mailer.time_mailer.get_clock() < max_nclo_algo_run:
           return False

    return True


def create_random_player(map_,id_, rnd_ability):

    return PlayerSimple(id_ =id_*-1 , current_location =map_.generate_location(), speed = speed,abilities=[rnd_ability])



def create_players(i):
    ans = []
    map1 = MapSimple(seed=i*10, length=length, width=width)

    abil_list = []
    for abil_number in range(max_number_of_missions):
        abil_list.append(AbilitySimple(ability_type=abil_number))

    for j in range(size_players):
        id_ = j+1
        if len(abil_list)!=0:
            abil = abil_list.pop()
        else:
            rnd = random.Random(id_ * 100 + i * 10)
            abil = AbilitySimple(ability_type=rnd.randint(0, max_number_of_missions - 1))

        player = create_random_player(map1,id_,abil)
        ans.append(player)
    return ans


def get_solver(communication_protocol):
    communication_f = communication_protocol.get_communication_disturbance
    data_fisher = get_data_fisher()
    rij_function = calculate_rij_abstract
    termination_function = f_termination_condition_all_tasks_converged

    if solver_number == 1:
        ans = FMC_ATA(f_termination_condition=termination_function,
                      f_global_measurements=data_fisher,
                      f_communication_disturbance=communication_f,
                      future_utility_function=rij_function,
                      counter_of_converges=counter_of_converges,
                      Threshold = Threshold
        )

    return ans


def get_communication_protocols():
    ans = []
    for a in alphas_LossExponent:
        ans.append(CommunicationProtocolLossExponent(alpha=a, delta_x=width, delta_y=length, std=10))
    for b in alphas_delays:
        ans.append(CommunicationProtocolDelayExponent(alpha=b, delta_x=width, delta_y=length, std=10))

    return ans



def find_relevant_measure_from_dict(nclo, data_map_of_measure):
    while nclo != 0:
        if nclo in data_map_of_measure.keys():
            return data_map_of_measure[nclo]
        else:
            nclo = nclo - 1
    return 0


def get_data_prior_statistic_fisher(data_):
    data_keys = []
    data_keys_t = get_data_fisher().keys()
    for k in data_keys_t:
        data_keys.append(k)

    data_prior_statistic = {}
    for measure_name in data_keys:
        data_prior_statistic[measure_name] = {}
        for nclo in range(0, max_nclo_algo_run, fisher_data_jumps):
            data_prior_statistic[measure_name][nclo] = []
            for rep in range(start,end):
                data_of_rep = data_[rep]
                data_map_of_measure = data_of_rep[measure_name]
                the_measure = find_relevant_measure_from_dict(nclo, data_map_of_measure)
                data_prior_statistic[measure_name][nclo].append(the_measure)

    return data_prior_statistic

def make_fisher_data(fisher_measures):
    data_prior_statistic = get_data_prior_statistic(fisher_measures)
    pass


if __name__ == '__main__':
    communication_protocols = get_communication_protocols()

    for communication_protocol in communication_protocols:
        fisher_measures = {}  # {number run: measurement}
        print(communication_protocol)
        for i in range(start, end):
            print("Simulation number = "+str(i))

            # --- simulation prep ---
            communication_protocol.set_seed(i)
            f_generate_message_disturbance = communication_protocol.get_communication_disturbance
            name = str(i)
            players_list = create_players(i)
            solver = get_solver(communication_protocol)
            map = MapSimple(seed=i*200, length=length, width=width)
            tasks_generator = SimpleTaskGenerator(max_number_of_missions=max_number_of_missions, map_=map, seed=i,
                                                  max_importance=max_importance, players_list =players_list)

            # --- simulation run ---
            sim = Simulation(name=name,
                             players_list=players_list,
                             solver=solver,
                             f_generate_message_disturbance=f_generate_message_disturbance,
                             tasks_generator=tasks_generator,
                             end_time=end_time,
                             number_of_initial_tasks=size_of_initial_tasks,
                             is_static=is_static,
                             debug_mode=False)
            #--- prep data ---
            single_fisher_measures = sim.solver.mailer.measurements
            fisher_measures[i] = single_fisher_measures

        print("start data ",communication_protocol)
        make_fisher_data(fisher_measures)


