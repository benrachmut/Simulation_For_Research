import pandas as pd


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


def make_dynamic_simulation(finished_tasks,start, end,communication_protocol,algo_name,length,width):
    dict_ = get_dict_dynamic(finished_tasks,communication_protocol,algo_name)
    basic_name = ",algo_"+algo_name+",comm_"+communication_protocol.name+",start_"+str(start)+",end_"+str(end)+","+str(int(length))+"x"+str(int(width))+".csv"
    basic_name = "dynamic"+basic_name
    raw_panda = pd.DataFrame.from_dict(dict_)
    raw_panda.to_csv(basic_name, sep=',')
    return dict_,basic_name
