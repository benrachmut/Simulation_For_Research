from create_excel_dynamic import make_dynamic_simulation
from general_communication_protocols import CommunicationProtocolDelayUniform, get_communication_protocols, \
    CommunicationProtocolPerfectCommunication
from general_data_fisher_market import get_data_fisher
from general_r_ij import calculate_rij_abstract
from simulation_abstract import SimulationV2
from simulation_abstract_components import AbilitySimple, PlayerSimple, MapSimple, SimpleTaskGenerator
import random

from solver_fmc_distributed_asy import FMC_ATA, FisherTaskASY
from solver_fmc_distributed_sy import FMC_TA, FMC_ATA_task_aware
import sys
import pandas as pd


is_static = False
solver_type_list = [1] # [1,2,3]

solver_type = None

debug_mode_full = False
debug_mode_light = True

x = 1
y =6


start = 0#x*y
end = 50#x*(y+1)

size_players = 60
end_time = sys.maxsize
size_of_initial_tasks = 10 # 25
limited_additional_tasks =15 #0

# 1000,5000  range(0,6000,50)  *****10000,50000 range(0,50000,500)
#max_nclo_algo_run_list= 20000
max_nclo_algo_run = None
max_nclo_algo_run_list = [0]#[10**8]#[0,1000,10000]
fisher_data_jumps = 10

pace_of_tasks_list = [1*(10**5)]

##--- map ---
central_location_multiplier = 1.5
length = 10**6
width = 10**6

initial_workload_multiple = 100000 # maybe change

##--- task generator ---
max_number_of_missions = 3
max_importance = 100000

##--- agents ---
speed = 1

# name,alpha,delta_x,delta_y,

counter_of_converges=3
Threshold=10**-5

algo_name = ""
# --- communication_protocols ---
cenralized_always_discovers_without_delay = None
is_with_timestamp = False
is_with_perfect_communication = False
constants_loss_distance = [] # e^-(alpha*d)
constants_delay_poisson_distance = [] # Pois(alpha^d) 1000, 10000, 100000
constants_delay_uniform_distance=[1000000] # U(0, alpha^d) 50000

constants_loss_constant=[] # prob
constants_delay_poisson = []# Pois(lambda)
constants_delay_uniform=[] # U(0,UB) #---


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


def create_random_player(map_,id_, rnd_abilities):
    return PlayerSimple(id_ =id_*-1 , current_location =map_.generate_location(), speed = speed,abilities=rnd_abilities)


def create_players(i,map1):
    ans = []
    #map1 = MapSimple(seed=i*10, length=length, width=width)
    #map1.generate_location()

    #for abil_number in range(max_number_of_missions):
    #    abil_list.append(AbilitySimple(ability_type=abil_number))

    for j in range(size_players):
        abil_list = []
        id_ = j + 1
        rnd = random.Random(id_ * 100 + i * 10)

        for abil_number in range (max_number_of_missions):
            rnd_number = rnd.random()
            if rnd_number<0.5:
                abil_list.append(AbilitySimple(ability_type=abil_number))

        if len(abil_list) ==0:
            abil_list.append(AbilitySimple(ability_type=rnd.randint(0, max_number_of_missions - 1)))



        player = create_random_player(map1,id_,abil_list)
        ans.append(player)
    return ans





def get_solver(communication_protocol_distributed):
    # 1. FMC_ATA distributed distributed (FMC_ATA with protocol + for centralized with protocol)
    # 2. centralistic (FMC_TA with pois (0) + for centralized with protocol)
    # 3. centralistic (FMC_TA with pois (0) + for centralized with protocol) all discover
    # 1. FMC_ATA semi taskaware distributed  (FMC_ATA with protocol + for centralized with protocol)




    communication_f = communication_protocol_distributed.get_communication_disturbance
    data_fisher = get_data_fisher()
    rij_function = calculate_rij_abstract
    termination_function = f_termination_condition_all_tasks_converged
    ans = None
    if solver_type == 1:
        ans = FMC_ATA(util_structure_level=1, f_termination_condition=termination_function,
                      f_global_measurements=data_fisher,
                      f_communication_disturbance=communication_f,
                      future_utility_function=rij_function,
                      counter_of_converges=counter_of_converges,
                      Threshold=Threshold, is_with_timestamp=is_with_timestamp)
        if is_static:
            algo_name_t = "FMC_ATA"
        else:
            algo_name_t = "FMC_ATA distributed"
        create_comm_aware_after_solver = False


    if solver_type == 2:
        ans  = FMC_TA(util_structure_level=1,f_termination_condition=termination_function,
                      f_global_measurements=data_fisher,
                      f_communication_disturbance=communication_f,
                      future_utility_function=rij_function,
                      counter_of_converges=counter_of_converges,
                      Threshold=Threshold
                      )

        if is_static:
            raise Exception("solver centralized cannot run if static")
        else:
            algo_name_t = "FMC_TA centralized"

        create_comm_aware_after_solver = True

    if solver_type == 3:
        ans = FMC_TA(util_structure_level=1, f_termination_condition=termination_function,
                     f_global_measurements=data_fisher,
                     f_communication_disturbance=communication_f,
                     future_utility_function=rij_function,
                     counter_of_converges=counter_of_converges,
                     Threshold=Threshold
                     )

        if is_static:
            algo_name_t = "FMC_TA"
        else:
            algo_name_t = "FMC_TA semi - distributed"

    if solver_type == 4:
        ans = FMC_ATA_task_aware(util_structure_level=1, f_termination_condition=termination_function,
                  f_global_measurements=data_fisher,
                  f_communication_disturbance=communication_f,
                  future_utility_function=rij_function,
                  counter_of_converges=counter_of_converges,
                  Threshold=Threshold
                  )

        if is_static:
            algo_name_t = "FMC_ATA_task_aware"
        else:
            algo_name_t = "FMC_ATA semi-distributed"


    return ans,algo_name_t


def create_simulation(simulation_number ,players_list,solver,tasks_generator,end_time,f_generate_message_disturbance,tasks_list ):
    # 1. FMC_ATA distributed distributed (FMC_TA with protocol + for centralized with protocol)
    # 2. centralistic (FMC_TA with pois (0) + for centralized with protocol)
    # 3. centralistic (FMC_TA with pois (0) + for centralized with protocol) all discover

    sim = SimulationV2(name=str(simulation_number),
                       players_list=players_list,
                       solver=solver,
                       f_generate_message_disturbance=f_generate_message_disturbance,
                       tasks_generator=tasks_generator,
                       end_time=end_time,
                       number_of_initial_tasks=size_of_initial_tasks,
                       is_static=is_static,
                       debug_mode_full=debug_mode_full,
                       debug_mode_light=debug_mode_light,
                       central_location_multiplier = central_location_multiplier,tasks_list = tasks_list)
    return sim


def get_communication_protocol_giver_solver(communication_protocol,solver_type_temp, simulation_number,is_with_timestamp ):



    communication_protocol_for_central = None
    communication_protocol_for_distributed = None

    if solver_type_temp == 1:
        communication_protocol_for_central = CommunicationProtocolPerfectCommunication()
        communication_protocol_for_distributed = communication_protocol.copy_protocol()

    if solver_type_temp == 2:

        communication_protocol_for_central = communication_protocol.copy_protocol()
        communication_protocol_for_distributed = CommunicationProtocolPerfectCommunication()

    if  solver_type_temp == 3:
        if is_static:
            communication_protocol_for_central = CommunicationProtocolPerfectCommunication()
            communication_protocol_for_distributed = communication_protocol.copy_protocol()
        else:
            communication_protocol_for_central = communication_protocol.copy_protocol()
            communication_protocol_for_distributed = communication_protocol.copy_protocol()

    if solver_type_temp == 4:
        if is_static:
            communication_protocol_for_central = CommunicationProtocolPerfectCommunication()
            communication_protocol_for_distributed = communication_protocol.copy_protocol()
        else:
            communication_protocol_for_central = communication_protocol.copy_protocol()
            communication_protocol_for_distributed = communication_protocol.copy_protocol()


    communication_protocol_for_central.set_seed(simulation_number)
    communication_protocol_for_distributed.set_seed(simulation_number)
    # communication_protocol.set_seed(i)
    # communication_protocol_for_central.is_with_timestamp = is_with_timestamp

    communication_protocol_for_distributed.is_with_timestamp = is_with_timestamp
    communication_protocol_for_central.is_with_timestamp = True

    communication_protocol_for_distributed.set_seed(i)
    communication_protocol_for_central.set_seed(i)

    return communication_protocol_for_central, communication_protocol_for_distributed


def create_dataframe(string_list):
    # Split each string by comma to get individual values
    values = [s.split(',') for s in string_list]

    # Create a DataFrame from the values
    df = pd.DataFrame(values)

    return df


def create_tasks_df(tasks_dict):
    list_of_str = []
    list_of_str.append("Simulation_Number,Task_id,Arrival_time")
    for sim_number, tasks_list_ in tasks_dict.items():
        for task in tasks_list_:
            new_line = str(sim_number) + "," + task.id_ + "," + str(task.arrival_time)
            list_of_str.append(new_line)
    df = create_dataframe(list_of_str)
    df.to_csv("Task_raw_data.csv", index=False)




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

    tasks_dict = {}
    for communication_protocol in communication_protocols:

        fisher_measures = {}  # {number run: measurement}
        finished_tasks = {}

        for pace_of_tasks in pace_of_tasks_list:
            for solver_type_temp in solver_type_list:
                if solver_type_temp == 5 and communication_protocol.get_type() == "Loss":
                    continue
                solver_type = solver_type_temp
                finished_tasks = {}

                for m_nclo_temp in max_nclo_algo_run_list:
                    max_nclo_algo_run = m_nclo_temp

                    for i in range(start, end):
                        print("---simulation number:",str(i),"Communication",communication_protocol,",pace_of_tasks",str(pace_of_tasks),",central_location_multiplier,",str(central_location_multiplier),"max_nclo",str(max_nclo_algo_run),"---")
                        # --- communication ----
                        communication_protocol_for_central, communication_protocol_for_distributed = get_communication_protocol_giver_solver(
                            communication_protocol = communication_protocol, solver_type_temp=solver_type_temp, simulation_number=i, is_with_timestamp =is_with_timestamp)

                        # --- players ----
                        map_for_players = MapSimple(seed=i * 17 + 15, length=length, width=width)
                        players_list = create_players(i,map_for_players)

                        # --- tasks ----
                        map_for_tasks = MapSimple(seed=i * (17*17) + 88, length=length, width=width)
                        tasks_generator = SimpleTaskGenerator(max_number_of_missions=max_number_of_missions, map_=map_for_tasks, seed=i*17,
                                                  max_importance=max_importance, players_list=players_list,beta=pace_of_tasks, initial_workload_multiple = initial_workload_multiple, limited_additional_tasks = limited_additional_tasks, initial_tasks_size= size_of_initial_tasks)
                        tasks_list = tasks_generator.create_tasks_for_simulation_list()
                        tasks_dict[i] = tasks_list

                        # --- solver ----
                        solver,algo_name = get_solver(communication_protocol_for_distributed)
                        print("***---***",algo_name,"***---***")

                        # --- simulation ----
                        sim = create_simulation(simulation_number = i, players_list=players_list, solver=solver,
                                                tasks_generator=tasks_generator, end_time=end_time,
                                                f_generate_message_disturbance=communication_protocol_for_central.get_communication_disturbance,tasks_list = tasks_list)

                        finished_tasks[i] = sim.finished_tasks_list
                        #single_fisher_measures = sim.solver.mailer.measurements
                        #fisher_measures[i] = single_fisher_measures
                    organized_data,name_ = make_dynamic_simulation(finished_tasks,start, end,communication_protocol,algo_name,length,width,max_nclo_algo_run,Threshold,size_players,
                                                                           size_of_initial_tasks,pace_of_tasks,central_location_multiplier)

                #make_fisher_data(fisher_measures, get_data_fisher, max_nclo_algo_run, fisher_data_jumps, start, end,
                 #                communication_protocol, algo_name, length, width, Threshold, name_)

                #make_dynamic_simulation_cumulative(communication_protocol, length, width, algo_name, max_nclo_algo_run,
                 #                                  Threshold, organized_data, fisher_data_jumps, name_,pace_of_tasks)

    #create_tasks_df(tasks_dict)


