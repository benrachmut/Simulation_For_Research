import simulation_abstract_components
from simulation_abstract_components import PlayerSimple, MissionSimple, TaskSimple


def get_normalized_distance(player_entity, task_entity):
    distance = simulation_abstract_components.calculate_distance(player_entity, task_entity)

    length_ = simulation_abstract_components.length_
    width_ = simulation_abstract_components.width_
    max_map_distance = (length_**2+width_**2)**0.5

    return distance/max_map_distance

def calculate_rij_abstract(player_entity :PlayerSimple, mission_entity:MissionSimple, task_entity:TaskSimple,
                                                 t_now=0):

    if player_entity.abilities[0] != mission_entity.abilities[0]:
        return 0
    importance_parameter= task_entity.importance

    #distance_parameter = (discount_factor**distance)
    normalize_distance = get_normalized_distance(player_entity, task_entity)
    distance_parameter = 1-normalize_distance

    abandonment_parameter = 0
    current_mission = player_entity.current_mission
    current_task = player_entity.current_task


    if current_mission is not None and current_task.id_ != task_entity.id_:
        remaining_workload_ratio = current_mission.remaining_workload/current_mission.initial_workload
        abandonment_parameter = \
            remaining_workload_ratio * (current_task.importance/3)

    return max(importance_parameter*distance_parameter-abandonment_parameter,100)