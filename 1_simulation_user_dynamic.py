from create_dynamic_simulation_cumulative import make_dynamic_simulation_cumulative
from create_excel_dynamic import make_dynamic_simulation
from general_communication_protocols import CommunicationProtocolDelayUniform, get_communication_protocols, \
    CommunicationProtocolPerfectCommunication
from general_data_fisher_market import get_data_fisher
from general_r_ij import calculate_rij_abstract
from simulation_abstract import SimulationDistributed, SimulationCentralized
from simulation_abstract_components import AbilitySimple, PlayerSimple, MapSimple, SimpleTaskGenerator
import random

from solver_fmc_distributed_asy import FMC_ATA, FisherTaskASY
from solver_fmc_distributed_sy import FMC_TA
import sys


# 1-centralistic (FMC_TA with pois (0) + for centralized with protocol)
# 2-distributed (FMC_TA with protocol + for centralized with protocol)
# 3-distributed (FMC_ATA task aware with protocol + for centralized with protocol)
# 4-distributed (FMC_ATA with protocol + for centralized pois (0))

simulation_type_list = [1]
simulation_type = None

debug_mode_full = False
debug_mode_light = True

start = 0
end = 5

size_players = 50
end_time = sys.maxsize
size_of_initial_tasks = 15
limited_additional_tasks = 15

# 1000,5000  range(0,6000,50)  *****10000,50000 range(0,50000,500)
#max_nclo_algo_run_list= 20000
max_nclo_algo_run = 1000000
fisher_data_jumps = 1000

pace_of_tasks = 30000
##--- map ---
length = 10**7
width = 10**7

initial_workload_multiple = 1000 # maybe cahnge

##--- task generator ---
max_number_of_missions = 3
max_importance = 1000

##--- agents ---
speed = 1000

# name,alpha,delta_x,delta_y,

counter_of_converges=2
Threshold=10**-3

algo_name = ""
# --- communication_protocols ---
is_with_timestamp = None
is_with_perfect_communication = True
constants_loss_distance = [] # e^-(alpha*d)
constants_delay_poisson_distance = [] # Pois(alpha^d)
constants_delay_uniform_distance=[] # U(0, alpha^d)

constants_loss_constant=[] # prob
constants_delay_poisson = []# Pois(lambda)
constants_delay_uniform=[0] # U(0,UB) #---

def f_termination_condition_all_tasks_converged(agents_algorithm, mailer):
    # TODO take care of only 1 task in system
    if mailer.time_mailer.get_clock() > max_nclo_algo_run:
        mailer.time_mailer.clock = max_nclo_algo_run
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


def create_players(i,map1):
    ans = []
    #map1 = MapSimple(seed=i*10, length=length, width=width)
    #map1.generate_location()
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

    if simulation_type == 1:
        ans = FMC_ATA(util_structure_level=1, f_termination_condition=termination_function,
                      f_global_measurements=data_fisher,
                      f_communication_disturbance=communication_f,
                      future_utility_function=rij_function,
                      counter_of_converges=counter_of_converges,
                      Threshold=Threshold, is_with_timestamp=False
                      )

        algo_name = "FMC_ATA distributed"

    if simulation_type == 2:
        cp = CommunicationProtocolDelayUniform(is_with_timestamp=False, ub = 0)
        cp.set_seed(1)
        func_cp= cp.get_communication_disturbance
        ans = FMC_TA(f_termination_condition=termination_function,
                      f_global_measurements=data_fisher,
                      f_communication_disturbance=func_cp,
                      future_utility_function=rij_function,
                      counter_of_converges=counter_of_converges,
                      Threshold=Threshold
                      )
        algo_name = "FMC_ATA centralized"


    return ans


def create_simulation(simulation_type,players_list,solver,tasks_generator,end_time,f_generate_message_disturbance):
    if simulation_type == 1:
        sim = SimulationDistributed(name=str(i),
                                    players_list=players_list,
                                    solver=solver,
                                    tasks_generator=tasks_generator,
                                    end_time=end_time,
                                    number_of_initial_tasks=size_of_initial_tasks,
                                    is_static=False,
                                    debug_mode_full=debug_mode_full,
                                    debug_mode_light=debug_mode_light)
    if simulation_type == 2:
        sim = SimulationCentralized(name=str(i),
                                    players_list=players_list,
                                    solver=solver,
                                    f_generate_message_disturbance=f_generate_message_disturbance,
                                    tasks_generator=tasks_generator,
                                    end_time=end_time,
                                    number_of_initial_tasks=size_of_initial_tasks,
                                    is_static=False,
                                    debug_mode_full=debug_mode_full,
                                    debug_mode_light=debug_mode_light)


    return sim


def get_communication_protocol_giver_solver(communication_protocol,simulation_type_temp, simulation_number,is_with_timestamp ):

    # 1-centralistic (FMC_TA with pois (0) + for centralized with protocol)
    # 2-distributed (FMC_TA with protocol + for centralized with protocol)
    # 3-distributed (FMC_ATA task aware with protocol + for centralized with protocol)
    # 4-distributed (FMC_ATA with protocol + for centralized pois (0))

    communication_protocol_for_central = None
    communication_protocol_for_distributed = None

    if simulation_type_temp == 1:
        communication_protocol_for_central = communication_protocol.copy_protocol()
        communication_protocol_for_distributed = CommunicationProtocolPerfectCommunication()

    if simulation_number == 2 or simulation_number == 3:
        communication_protocol_for_central = communication_protocol.copy_protocol()
        communication_protocol_for_distributed = communication_protocol.copy_protocol()

    if simulation_number == 4:
        communication_protocol_for_central = CommunicationProtocolPerfectCommunication()
        communication_protocol_for_distributed = communication_protocol.copy_protocol()

    # communication_protocol.set_seed(i)
    # communication_protocol_for_central.is_with_timestamp = is_with_timestamp

    communication_protocol_for_distributed.is_with_timestamp = is_with_timestamp
    communication_protocol_for_central.is_with_timestamp = False

    communication_protocol.set_seed(i)
if __name__ == '__main__':

    communication_protocols = get_communication_protocols(
        is_with_timestamp=is_with_timestamp,length=length,width=width,
        is_with_perfect_communication = is_with_perfect_communication,constants_loss_distance=constants_loss_distance,
        constants_delay_poisson_distance=constants_delay_poisson_distance,
        constants_delay_uniform_distance=constants_delay_uniform_distance,
        constants_loss_constant=constants_loss_constant,
        constants_delay_poisson=constants_delay_poisson,
        constants_delay_uniform=constants_delay_uniform)
    price_dict = {}

    for communication_protocol in communication_protocols:






        fisher_measures = {}  # {number run: measurement}
        finished_tasks = {}
        for simulation_type_temp in simulation_type_list:




            simulation_type = simulation_type_temp
            finished_tasks = {}
            for i in range(start, end):
                print("simulation number:",str(i),"Communication",communication_protocol_for_distributed)
                communication_protocol_for_central, communication_protocol_for_distributed = get_communication_protocol_giver_solver(
                    communication_protocol =communication_protocol, simulation_type_temp=simulation_type_temp,simulation_number=i, is_with_timestamp =is_with_timestamp)

                map_for_players = MapSimple(seed=i * 17, length=length, width=width)
                players_list = create_players(i,map_for_players)
                f_generate_message_disturbance = communication_protocol.get_communication_disturbance
                solver = get_solver(communication_protocol)

                map_for_players = MapSimple(seed=i * (17*17), length=length, width=width)
                tasks_generator = SimpleTaskGenerator(max_number_of_missions=max_number_of_missions, map_=map, seed=i*17,
                                          max_importance=max_importance, players_list=players_list,beta=pace_of_tasks, initial_workload_multiple = initial_workload_multiple, limited_additional_tasks = limited_additional_tasks)

                sim = create_simulation(simulation_type= simulation_type,players_list=players_list,solver=solver,
                                        tasks_generator=tasks_generator,end_time=end_time,
                                        f_generate_message_disturbance=f_generate_message_disturbance)

                finished_tasks[i] = sim.finished_tasks_list
            organized_data,name_ = make_dynamic_simulation(finished_tasks,start, end,communication_protocol,algo_name,length,width,max_nclo_algo_run,Threshold,size_players,
                                                                   size_of_initial_tasks)
            make_dynamic_simulation_cumulative(communication_protocol, length, width, algo_name, max_nclo_algo_run,
                                               Threshold, organized_data, fisher_data_jumps, name_)
