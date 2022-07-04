import pandas as pd

from create_excel_fisher import add_stuff_to_dictionary, get_value_list_size


def get_dict_dynamic(finished_tasks, communication_protocol,algo_name):
    protocol_type = communication_protocol.type_
    protocol_name = communication_protocol.name
    ans = {}
    ans["protocol_type"] = []
    ans["protocol_name"] = []
    ans["Algorithm"] = []
    ans["Simulation_Number"] = []

    for run_number, tasks in finished_tasks.items():
        for task in tasks:
            for mission in task.done_missions:
                ans["protocol_type"].append(protocol_type)
                ans["protocol_name"].append(protocol_name)
                ans["Algorithm"].append(algo_name)
                ans["Simulation_Number"].append(run_number)
                dict_ = mission.measurements.get_mission_measurements_dict()
                for measure_name, measure_number in dict_.items():
                    if measure_name not in ans.keys():
                        ans[measure_name] = []
                    ans[measure_name].append(measure_number)


    return ans



def add_more_info(communication_protocol,length,width,algo_name,max_nclo_algo_run,converge_threshold,pace_of_tasks,central_location_multiplier_list,dict_):
    protocol_type = communication_protocol.type_
    protocol_name = communication_protocol.name
    if communication_protocol.is_with_timestamp:
        timestamp = "TS"
    else:
        timestamp = ""

    map_size = str(int(length)) + "X" + str(int(width))


    what_to_add = {"protocol_type":protocol_type,"protocol_name":protocol_name,
                   "Algorithm":algo_name,"map_size":map_size,"max_nclo":max_nclo_algo_run,
                   "converge_threshold":converge_threshold, "Time Stamp":timestamp,"pace of tasks": pace_of_tasks,"central_location_multiplier_list":central_location_multiplier_list}

    value_size = get_value_list_size(dict_)
    add_stuff_to_dictionary(what_to_add,value_size,dict_)

def make_dynamic_simulation(finished_tasks,start, end,communication_protocol,algo_name,length,width,max_nclo_algo_run,converge_threshold,num_players,num_tasks,pace_of_tasks,central_location_multiplier_list):
    dict_ = get_dict_dynamic(finished_tasks,communication_protocol,algo_name)
    add_more_info(communication_protocol,length,width,algo_name,max_nclo_algo_run,converge_threshold,pace_of_tasks,central_location_multiplier_list,dict_)



    basic_name = ",algo_" + algo_name + ",comm_" + communication_protocol.name + ",start_" + str(start) + ",end_" + str(
        end) + ",maxNclo_" + str(
        max_nclo_algo_run) + ",threshold_" + str(converge_threshold) +","+str(communication_protocol.is_with_timestamp)+",numPlayers_"+str(num_players)+",numTasks"+\
                 str(num_tasks)+",pace_of_tasks_"+str(pace_of_tasks)+",central_location_"+str(central_location_multiplier_list)+".csv"


    file_name = "dynamic"+basic_name
    raw_panda = pd.DataFrame.from_dict(dict_)
    raw_panda.to_csv(file_name, sep=',')
    return dict_,basic_name