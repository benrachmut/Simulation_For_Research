import random

from general_communication_protocols import CommunicationProtocolLossExponent, CommunicationProtocolDelayExponent
from general_data_fisher_market import get_data_fisher
from general_r_ij import calculate_rij_abstract
from simulation_abstract import Simulation
from simulation_abstract_components import SimpleTaskGenerator, MapSimple, PlayerSimple, AbilitySimple
from solver_fmc import FMC_ATA, FisherTaskASY

start = 0
end = 100
size_players = 10
end_time = 100000
size_of_initial_tasks = 10
max_nclo = 1000

##--- 1 = distributed FMC_ATA;  ---
solver_number = 1


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
    if mailer.time_mailer.get_clock() > max_nclo:
        return True

    tasks = []
    players = []
    for agent in agents_algorithm:
        if isinstance(agent,FisherTaskASY):
            tasks.append(agent)
        else:
            players.append(agent)

    for task in tasks:
        if not task.is_finish_phase_II and mailer.time_mailer.get_clock() < max_nclo:
           return False

    return True


def create_random_player(map_,id_,i):
    rnd = random.Random(id_*100+i*10)
    rnd_ability = AbilitySimple(ability_type = rnd.randint(0,max_number_of_missions-1))
    return PlayerSimple(id_ =id_*-1 , current_location =map_.generate_location(), speed = speed,abilities=[rnd_ability])



def create_players(i):
    ans = []
    map1 = MapSimple(seed=i*10, length=length, width=width)




    for j in range(size_players):
        id_ = j+1
        player = create_random_player(map1,id_,i)
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
                      future_utility_function=rij_function)

    return ans


def get_communication_protocols():
    ans = []
    for a in alphas_LossExponent:
        ans.append(CommunicationProtocolLossExponent(alpha=a, delta_x=width, delta_y=length, std=10))
    for b in alphas_delays:
        ans.append(CommunicationProtocolDelayExponent(alpha=b, delta_x=width, delta_y=length, std=10))

    return ans


if __name__ == '__main__':
    communication_protocols = get_communication_protocols()


    for i in range(start, end):
        print("Simulation number = "+str(i))
        for communication_protocol in communication_protocols:
            print(communication_protocol)

            communication_protocol.set_seed(i)
            f_generate_message_disturbance = communication_protocol.get_communication_disturbance
            name = str(i)
            players_list = create_players(i)
            solver = get_solver(communication_protocol)
            map = MapSimple(seed=i*200, length=length, width=width)

            tasks_generator = SimpleTaskGenerator(max_number_of_missions=max_number_of_missions, map_=map, seed=i,
                                                  max_importance=max_importance, players_list =players_list)

            sim = Simulation(name=name,
                             players_list=players_list,
                             solver=solver,
                             f_generate_message_disturbance=f_generate_message_disturbance,
                             tasks_generator=tasks_generator,
                             end_time=end_time,
                             number_of_initial_tasks=size_of_initial_tasks,
                             is_static=True,
                             debug_mode=False)
