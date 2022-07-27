
import pandas as pd


def find_relevant_measure_from_dict(nclo, data_map_of_measure,):
    while nclo != 0:
        if nclo in data_map_of_measure.keys():
            return data_map_of_measure[nclo]
        else:
            nclo = nclo - 1
    return 0

def get_data_prior_statistic_fisher(data_,get_data_fisher,max_nclo_algo_run, fisher_data_jumps,start,end):
    data_keys = []
    data_keys_t = get_data_fisher().keys()
    for k in data_keys_t:
        data_keys.append(k)

    data_prior_statistic = {}
    for measure_name in data_keys:
        data_prior_statistic[measure_name] = {}
        for nclo in range(0, max_nclo_algo_run, fisher_data_jumps):
            data_prior_statistic[measure_name][nclo] = []
            for rep in range(start,end):
                data_of_rep = data_[rep]
                data_map_of_measure = data_of_rep[measure_name]
                the_measure = find_relevant_measure_from_dict(nclo, data_map_of_measure)
                data_prior_statistic[measure_name][nclo].append(the_measure)

    return data_prior_statistic

def get_avg_fisher(data_prior_statistic,get_data_fisher):
    data_keys = get_data_fisher().keys()
    ans = {}
    for key in data_keys:
        ans[key] = {}
        data_per_nclo = data_prior_statistic[key]
        for nclo, measure_list in data_per_nclo.items():
            ans[key][nclo] = sum(measure_list) / len(measure_list)
    return ans

def get_data_avg_before_excel(data_avg):
    ans = {}

    for title, nclo_dict in data_avg.items():
        nclo_list = []
        for nclo, single_measure in nclo_dict.items():
            nclo_list.append(nclo)
        ans["NCLO"] = nclo_list
        break

    for title, nclo_dict in data_avg.items():
        measure_list = []
        for nclo, single_measure in nclo_dict.items():
            measure_list.append(single_measure)
        ans[title] = measure_list

    return ans

def get_data_last_before_excel(data_):
    ans = {}
    for measure_name,nclo_dict in data_.items():
        max_nclo = max(nclo_dict.keys())
        ans[measure_name] = nclo_dict[max_nclo]
    return ans

def get_data_time_converged_before_excel(fisher_measures):
    ans = {}
    ans["id_"] = []
    ans["converge_time"] = []
    for num_run,dict_measures in fisher_measures.items():
        ans["id_"].append(num_run)
        for measure_name,dict_nclo_and_numbers in dict_measures.items():
            converge_time = max(dict_nclo_and_numbers.keys())
            ans["converge_time"].append(converge_time)
            break
    return ans

def process_data_before_excel(fisher_measures,get_data_fisher,max_nclo_algo_run, fisher_data_jumps,start,end):
    data_prior_statistic = get_data_prior_statistic_fisher(fisher_measures, get_data_fisher, max_nclo_algo_run,
                                                           fisher_data_jumps, start, end)
    data_avg = get_avg_fisher(data_prior_statistic, get_data_fisher)
    data_avg_before_excel = get_data_avg_before_excel(data_avg)
    data_last_before_excel = get_data_last_before_excel(data_prior_statistic)
    data_time_converged_before_excel = get_data_time_converged_before_excel(fisher_measures)

    return data_avg_before_excel,data_last_before_excel,data_time_converged_before_excel

def add_stuff_to_dictionary(what_to_add,required_size,dict_):
    for measure_name, measure_value in what_to_add.items():
        list_ = []
        for _ in range(required_size):
            list_.append(measure_value)
        dict_[measure_name] = list_

def get_value_list_size(dict_):
    for k,v in dict_.items():
        return len(v)

def add_communication_protocol_and_algo(data_avg_before_excel, data_last_before_excel, data_time_converged_before_excel,
                                        communication_protocol,algo_name,length,width,max_nclo_algo_run,converge_threshold):
    protocol_type = communication_protocol.type_
    protocol_name = communication_protocol.name
    map_size = str(int(length))+"X"+str(int(width))

    what_to_add = {"protocol_type":protocol_type,"protocol_name":protocol_name,
                   "Algorithm":algo_name,"map_size":map_size,"max_nclo":max_nclo_algo_run,"converge_threshold":converge_threshold}

    value_size = get_value_list_size(data_avg_before_excel)
    add_stuff_to_dictionary(what_to_add,value_size,data_avg_before_excel)

    value_size = get_value_list_size(data_last_before_excel)
    add_stuff_to_dictionary(what_to_add, value_size, data_last_before_excel)

    value_size = get_value_list_size(data_time_converged_before_excel)
    add_stuff_to_dictionary(what_to_add, value_size, data_time_converged_before_excel)



def create_excel_fisher(basic_name, data_avg_before_excel, data_last_before_excel, data_time_converged_before_excel):

    avg_panda = pd.DataFrame.from_dict(data_avg_before_excel)
    avg_panda.to_csv("avg"+basic_name, sep=',')

    #last_panda = pd.DataFrame.from_dict(data_last_before_excel)
    #last_panda.to_csv("last"+basic_name, sep=',')

    converge_panda = pd.DataFrame.from_dict(data_time_converged_before_excel)
    converge_panda.to_csv("converge"+basic_name, sep=',')


def make_fisher_data(fisher_measures,get_data_fisher,max_nclo_algo_run, fisher_data_jumps,start,end,communication_protocol,algo_name,length,width,converge_threshold,basic_name):
    data_avg_before_excel,data_last_before_excel,data_time_converged_before_excel = process_data_before_excel(fisher_measures,get_data_fisher,max_nclo_algo_run, fisher_data_jumps,start,end)
    add_communication_protocol_and_algo(data_avg_before_excel, data_last_before_excel, data_time_converged_before_excel, communication_protocol, algo_name,length,width,max_nclo_algo_run,converge_threshold)
    #basic_name = ",algo_"+algo_name+",comm_"+communication_protocol.name+",start_"+str(start)+",end_"+str(end)\
    #             +","+str(int(length))+"x"+str(int(width))+",maxNclo_"+str(max_nclo_algo_run)+",threshold_"+str(converge_threshold)+".csv"
    create_excel_fisher(basic_name,data_avg_before_excel,data_last_before_excel,data_time_converged_before_excel)
