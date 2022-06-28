import simulation_abstract_components
from simulation_abstract_components import PlayerSimple, MissionSimple, TaskSimple



def get_normalized_distance(player_entity, task_entity):
    distance = simulation_abstract_components.calculate_distance(player_entity, task_entity)

    length_ = simulation_abstract_components.length_
    width_ = simulation_abstract_components.width_
    max_map_distance = (length_**2+width_**2)**0.5

    return distance/max_map_distance


def agent_was_present(mission_entity):
    if mission_entity.measurements.x1_simulation_time_first_player_arrive is None:
        return False
    return True


def calculate_rij_abstract(player_entity :PlayerSimple, mission_entity:MissionSimple, task_entity:TaskSimple,
                                                 t_now=0):

    if player_entity.abilities[0] != mission_entity.abilities[0]:
        return 0
    importance_parameter= task_entity.importance

    #distance_parameter = (discount_factor**distance)
    #normalize_distance = get_normalized_distance(player_entity, task_entity)
    distance =  simulation_abstract_components.calculate_distance(player_entity, task_entity)
    speed = player_entity.speed
    arrive_time = distance/speed

    if agent_was_present(mission_entity):
        travel_factor = simulation_abstract_components.travel_factor_agent_was_present
    else:
        travel_factor = simulation_abstract_components.travel_factor

    travel_factor_normalized = simulation_abstract_components.travel_factor_normalized

    distance_parameter = travel_factor**(arrive_time / travel_factor_normalized)
    abandonment_parameter = 0
    current_mission = player_entity.current_mission
    current_task = player_entity.current_task


    if current_mission is not None and current_task.id_ != task_entity.id_:
        remaining_workload_ratio = current_mission.remaining_workload/current_mission.initial_workload
        abandonment_parameter = \
            remaining_workload_ratio * (current_task.importance / (simulation_abstract_components.abandonment_factor*0.25))

    return max(importance_parameter*distance_parameter-abandonment_parameter,1)