import random
import sys

from create_dynamic_simulation_cumulative import make_dynamic_simulation_cumulative
from create_excel_dynamic import make_dynamic_simulation
from create_excel_fisher import make_fisher_data
from general_communication_protocols import CommunicationProtocolLossExponent, \
    CommunicationProtocolDelayDistancePoissonExponent, get_communication_protocols
from general_data_fisher_market import get_data_fisher
from general_r_ij import calculate_rij_abstract
from simulation_abstract import SimulationV1
from simulation_abstract_components import SimpleTaskGenerator, MapSimple, PlayerSimple, AbilitySimple
from solver_fmc_centralized import  FisherCentralizedPrice

from solver_fmc_distributed_asy import FMC_ATA, FisherTaskASY  # , FMC_TA
from solver_fmc_distributed_sy import FMC_TA, FMC_ATA_task_aware





is_static =True
start = 0
end = 100
size_players = 50

end_time = sys.maxsize
size_of_initial_tasks =30
# 1000,5000  range(0,6000,50)  *****10000,50000 range(0,50000,500)
max_nclo_algo_run_list= [8000,3000]
max_nclo_algo_run = None
fisher_data_jumps = 1000

##--- 1 = FMC_ATA; 2 = FMC_ATA_task_aware ; 3 = FMC_ATA rand rij; 4 = FMC_TA---
solver_number_list = [4]
solver_number = None
is_with_fisher_data = False

# --- communication_protocols ---
is_with_timestamp = None
constants_loss_distance = [] # e^-(alpha*d)
constants_delay_poisson_distance = [0] # Pois(alpha^d)
constants_delay_uniform_distance=[] # U(0, alpha^d)

constants_loss_constant=[] # prob
constants_delay_poisson = [] # Pois(lambda)
constants_delay_uniform=[] # U(0,UB) #---



##--- map ---
length = 10**6
width = 10**6

initial_workload_multiple = 10000 # maybe change

##--- task generator ---
max_number_of_missions = 3
max_importance = 10000

##--- agents ---
speed = 1

# name,alpha,delta_x,delta_y,

counter_of_converges=1
Threshold=10**-200

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

    if solver_number == 1:
        ans = FMC_ATA(util_structure_level= 1,f_termination_condition=termination_function,
                      f_global_measurements=data_fisher,
                      f_communication_disturbance=communication_f,
                      future_utility_function=rij_function,
                      counter_of_converges=counter_of_converges,
                      Threshold = Threshold,is_with_timestamp= is_with_timestamp
        )

    if solver_number == 2:
        ans = FMC_ATA_task_aware(util_structure_level=1, f_termination_condition=termination_function,
                      f_global_measurements=data_fisher,
                      f_communication_disturbance=communication_f,
                      future_utility_function=rij_function,
                      counter_of_converges=counter_of_converges,
                      Threshold=Threshold,is_with_timestamp= is_with_timestamp
                      )

    if solver_number == 3:
        ans = FMC_ATA(util_structure_level=3, f_termination_condition=termination_function,
                      f_global_measurements=data_fisher,
                      f_communication_disturbance=communication_f,
                      future_utility_function=rij_function,
                      counter_of_converges=counter_of_converges,
                      Threshold=Threshold
                      )

    if solver_number == 4:
        ans = FMC_TA(f_termination_condition=termination_function,
                      f_global_measurements=data_fisher,
                      f_communication_disturbance=communication_f,
                      future_utility_function=rij_function,
                      counter_of_converges=counter_of_converges,
                      Threshold=Threshold
                      )
    global algo_name
    algo_name= ans.__str__()

    return ans





def print_players(players_list):
    for p in players_list:
        print("id:",p.id_,", ability:",p.abilities[0].ability_type,", location",p.location)


def print_initial_tasks(tasks_generator):

    tasks_list = tasks_generator.get_tasks_number_of_tasks_now(0,size_of_initial_tasks)

    for task in tasks_list:
        print("***--- id:",task.id_,", location:",task.location," importance:",task.importance,"---***")
        for mission in task.missions_list:
            print("id:", mission.mission_id, ", workload:", mission.initial_workload,
                  ", ability:",mission.abilities[0].ability_type, ", max amount:",mission.max_players)





def get_price_vector(i):
    map = MapSimple(seed=i * 200, length=length, width=width)
    players_list = create_players(i)
    tasks_generator = SimpleTaskGenerator(max_number_of_missions=max_number_of_missions, map_=map, seed=i,
                                          max_importance=max_importance, players_list=players_list)

    tasks_list = tasks_generator.get_tasks_number_of_tasks_now(0,size_of_initial_tasks)
    rij_function = calculate_rij_abstract

    solv = FisherCentralizedPrice(THRESHOLD = Threshold, future_utility_function= rij_function, tasks_simulation = tasks_list, players_simulation = players_list)
    return solv.get_price_vector()


def run_simulation(i):
    communication_protocol.set_seed(i)
    f_generate_message_disturbance = communication_protocol.get_communication_disturbance
    name = str(i)
    map = MapSimple(seed=i * 17, length=length, width=width)

    players_list = create_players(i,map)

    tasks_generator = SimpleTaskGenerator(max_number_of_missions=max_number_of_missions, map_=map, seed=i*20,
                                          max_importance=max_importance, players_list=players_list, initial_workload_multiple = initial_workload_multiple)
    solver = get_solver(communication_protocol)
    #print_initial_tasks(tasks_generator)
    # --- simulation run ---
    sim = SimulationV1(name=name,
                       players_list=players_list,
                       solver=solver,
                       tasks_generator=tasks_generator,
                       end_time=end_time,
                       number_of_initial_tasks=size_of_initial_tasks,
                       is_static=is_static,
                       debug_mode_light=False, debug_mode_full=False)
    return sim


if __name__ == '__main__':

    communication_protocols = get_communication_protocols(
        is_with_timestamp=is_with_timestamp,length=length,width=width,
        constants_loss_distance=constants_loss_distance,
        constants_delay_poisson_distance=constants_delay_poisson_distance,
        constants_delay_uniform_distance=constants_delay_uniform_distance,
        constants_loss_constant=constants_loss_constant,
        constants_delay_poisson=constants_delay_poisson,
        constants_delay_uniform=constants_delay_uniform)
    price_dict = {}

    for t_ in max_nclo_algo_run_list:
        max_nclo_algo_run = t_
        for solver_number_t in solver_number_list:
            solver_number = solver_number_t
            is_with_timestamp_list = [False]
            if solver_number <= 2:
                is_with_timestamp_list = [False]
            for is_with_timestamp_t in is_with_timestamp_list:
                is_with_timestamp = is_with_timestamp_t
                for communication_protocol in communication_protocols:
                    communication_protocol.is_with_timestamp = is_with_timestamp
                    fisher_measures = {}  # {number run: measurement}
                    finished_tasks ={}
                    print(communication_protocol)
                    print("solver_number ",str(solver_number))
                    print("max_nclo_algo_run ",str(max_nclo_algo_run))

                    for i in range(start, end):
                        print("Simulation number = "+str(i))
                        # print_players(players_list)

                        #if i not in price_dict.keys():
                        #    price_vector = get_price_vector(i)
                        #    price_dict[i] = price_vector
                        sim = run_simulation(i)

                        #--- prep data ---
                        single_fisher_measures = sim.solver.mailer.measurements
                        fisher_measures[i] = single_fisher_measures
                        finished_tasks[i] = sim.finished_tasks_list
                    print("start data ",communication_protocol)

                    organized_data,name_ = make_dynamic_simulation(finished_tasks=finished_tasks,start =start, end=end,communication_protocol =communication_protocol,algo_name =algo_name,length =length,width =width,max_nclo_algo_run =max_nclo_algo_run,converge_threshold =Threshold,num_players =size_players,
                                                                   num_tasks =size_of_initial_tasks, pace_of_tasks = 0, central_location_multiplier_list = 0 )




                    if is_with_fisher_data:
                        make_fisher_data(fisher_measures,get_data_fisher, max_nclo_algo_run, fisher_data_jumps, start, end,communication_protocol,algo_name,length,width,Threshold,name_)
                        #make_dynamic_simulation_cumulative(communication_protocol=communication_protocol,length =length,width=width,algo_name=algo_name,max_nclo_algo_run =max_nclo_algo_run,converge_threshold= Threshold,organized_data = organized_data,fisher_data_jumps = fisher_data_jumps,name_ = name_,pace_of_tasks =0)
