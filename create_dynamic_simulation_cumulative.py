def get_max_time_in_system(organized_data):
    total_time_in_system = []
    for ttt in (organized_data["Total Time In System"]):
        if isinstance(ttt, float):
            total_time_in_system.append(ttt)
    return max(total_time_in_system)

def get_data_scenario_by_index(organized_data):
    ans = {}
    counter = 0
    for sim_num in organized_data["Simulation_Number"]:
        if sim_num not in ans.keys():
            ans[sim_num] = []
        ans [sim_num].append(counter)
        counter = counter +1
    return ans



def get_data_grouped_by_scenario(organized_data, data_scenario_by_index,keys):
    ans = {}
    for scenario_number, index_list in data_scenario_by_index.items():
        ans[scenario_number] = {}

        for key in keys:
            if key not in ans[scenario_number]:
                ans[scenario_number][key] = []
            temp_ = organized_data[key]
            for i in index_list:
                ans[scenario_number][key].append(temp_[i])
    return ans


def get_data_scenario_by_index_by_importance(organized_data):
    ans = {}
    by_index = get_data_scenario_by_index(organized_data)
    for sim_number, index_list in by_index.items():
        if sim_number not in ans:
            ans[sim_number] = {}
        for i in index_list:
            importance = organized_data["Task Importance"][i]
            importance2 = int(importance/1000)
            if importance2 not in  ans[sim_number]:
                ans[sim_number][importance2] = []
            ans[sim_number][importance2].append(i)
    return ans



    return ans


def get_group_by_scenario_by_importance(organized_data, data_scenario_by_index, keys):
    pass


def get_data_time_simNumber_indexs(data_group_by_scenario_via_list,max_time,fisher_data_jumps):
    ans = {}
    for time_ in range(0, int(max_time *1.5), fisher_data_jumps*2):
        ans[time_] = {}
        for sim_number, dict_measure_listData in data_group_by_scenario_via_list.items():
            ans[time_][sim_number] = []
            total_time_in_system_list = dict_measure_listData["Total Time In System"]
            counter = 0
            for total_time_in_system in total_time_in_system_list:
                if isinstance(total_time_in_system, float):

                    if total_time_in_system < time_:
                        ans[time_][sim_number].append(counter)
                counter = counter + 1
    return ans


def get_data_prior_cumulative(data_time_simNumber_indexs, data_group_by_scenario_via_list,keys):
    ans = {}
    for time_,scenario_number_and_index_list in data_time_simNumber_indexs.items():
        ans[time_] = {}
        for sim_number,index_list in scenario_number_and_index_list.items():
            ans[time_][sim_number] ={}
            for key in keys:
                if key!="Total Time In System":
                    ans[time_][sim_number][key] = []
                    for i in index_list:
                        ans[time_][sim_number][key].append(data_group_by_scenario_via_list[sim_number][key][i])
    return ans


def get_data_cumulative_dict(data_prior_cumulative):
    ans= {}
    for time_, scenario_number_dict in data_prior_cumulative.items():
        ans[time_] = {}
        for scenario_number,measure_data_dict in scenario_number_dict.items():
            for measure_,data_list in measure_data_dict.items():
                if measure_ not in ans[time_]:
                    ans[time_][measure_] = []
                if len(data_list) == 0:
                    ans[time_][measure_].append(0)
                else:
                    ans[time_][measure_].append(sum(data_list))
    return ans


def calculate_avg_data_cumulative(data_cumulative_dict):
    pass


def make_dynamic_simulation_cumulative(organized_data ,fisher_data_jumps,name_,keys =
        ["Total Time In System","Arrival Delay","Cap","Abandonment Penalty"]):

    max_time = int(get_max_time_in_system(organized_data))+1

    data_scenario_by_index = get_data_scenario_by_index(organized_data)
    data_group_by_scenario_via_list = get_data_grouped_by_scenario(organized_data,data_scenario_by_index,keys)

    #data_scenario_by_index_by_importance = get_data_scenario_by_index_by_importance(organized_data)
    #data_group_by_scenario_by_importance_via_list = get_group_by_scenario_by_importance(organized_data,data_scenario_by_index,keys)

    data_time_simNumber_indexs = get_data_time_simNumber_indexs(data_group_by_scenario_via_list,max_time,fisher_data_jumps)
    data_prior_cumulative = get_data_prior_cumulative(data_time_simNumber_indexs, data_group_by_scenario_via_list,keys)
    data_cumulative_dict = get_data_cumulative_dict(data_prior_cumulative)
    data_cumulative_dict_for_panda = calculate_avg_data_cumulative(data_cumulative_dict)

