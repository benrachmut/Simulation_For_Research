from communication_protocols import CommunicationProtocolLossExponent, CommunicationProtocolDelayExponent
from simulation_abstract import Simulation
from simulation_abstract_components import SimpleTaskGenerator, MapSimple, PlayerSimple

start = 0
end = 100
size_players = 50
end_time = 100000
size_of_initial_tasks = 10

##--- 1 = distributed FMC_ATA;  ---
solver_number = 1


# --- communication_protocols ---
std = 10
alphas_LossExponent = [0.1, 0.5, 1, 1.5, 2, 5, 10]
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

def create_random_player(map_,id_):
    return PlayerSimple(id_ =id_*-1 , current_location =map_.generate_location(), speed = speed)



def create_players(i):
    ans = []
    map1 = MapSimple(seed=i*10, length=length, width=width)




    for j in range(size_players):
        player = create_random_player(map1,j)
        ans.append(player)
    return ans


def get_solver():
    # TODO
    pass


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
        for communication_protocol in communication_protocols:
            communication_protocol.set_seed(i)
            f_generate_message_disturbance = communication_protocol.get_communication_disturbance
            name = str(i)
            players_list = create_players(i)
            solver = get_solver(i)
            map = MapSimple(seed=i*200, length=length, width=width)

            tasks_generator = SimpleTaskGenerator(max_number_of_missions=max_number_of_missions, map_=map, seed=i,
                                                  max_importance=max_importance)

            sim = Simulation(name=name,
                             players_list=players_list,
                             solver=solver,
                             f_generate_message_disturbance=f_generate_message_disturbance,
                             tasks_generator=tasks_generator,
                             end_time=end_time,
                             number_of_initial_tasks=size_of_initial_tasks,
                             is_static=True,
                             debug_mode=False)
