NCLO_jumps = 100000
NCLO_max = 50000000
import os
import pandas as pd
import statistics


folder_path = r'C:\Users\Ben\Desktop\CADCOP data II\v18 journal fisher'  # Replace with the path to your folder
raw_task_data = pd.read_csv(folder_path+"\\"+"Task_raw_data.csv")
folder_path = r'C:\Users\Ben\Desktop\dynamic'  # Replace with the path to your folder


def concatenate_csv_lines(file_list,temp_path):
    concatenated_lines = []

    for file_name in file_list:
        dir_ = os.path.join(temp_path, file_name)
        #dynamic, algo_FMC_ATA
        #distributed, comm_Pois(
        #    1000000 ^ d), start_0, end_2, maxNclo_100000000, threshold_1e - 05, False, numPlayers_60, numTasks10, pace_of_tasks_100000, central_location_2
        with open(dir_, 'r') as csv_file:
            csv_reader = pd.read_csv(csv_file)
            concatenated_lines.append(csv_reader)
    concatenated_df = pd.concat(concatenated_lines)

    return concatenated_df

def create_nclo_dict(unique_num_runs,df,field_name):
    nclo_dict={}
    for run in unique_num_runs:
            df_per_run = df[df["Simulation_Number"] == run]
            for NCLO in range(0, NCLO_max, NCLO_jumps):
                selected_rows = df_per_run[( df_per_run["End_time"] < NCLO)][field_name]
                sum_per_NCLO = sum(selected_rows.tolist())
                if NCLO not in nclo_dict:
                    nclo_dict[NCLO] = []
                nclo_dict[NCLO].append(sum_per_NCLO)
    return  nclo_dict


def create_nclo_dict_for_updated_delay(unique_num_runs,df,field_name):
    nclo_dict={}
    for run in unique_num_runs:
            df_per_run = df[df["Simulation_Number"] == run]
            for NCLO in range(0, NCLO_max, NCLO_jumps):
                selected_rows = df_per_run[( df_per_run["Arrival_time"] < NCLO)]
                if selected_rows.empty:
                    sum_per_NCLO = 0
                else:
                    result_list = selected_rows.apply(
                        lambda row: NCLO - row['Arrival_time'] if NCLO < row['Time_of_First_Arrive'] else
                        row['Arrival Delay'], axis=1).tolist()

                    sum_per_NCLO = sum(result_list)
                if NCLO not in nclo_dict:
                    nclo_dict[NCLO] = []
                nclo_dict[NCLO].append(sum_per_NCLO)
    return  nclo_dict

def create_nclo_dict_finish(unique_num_runs, df, field_name):
    nclo_dict = {}
    for run in unique_num_runs:
        df_per_run = df[df["Simulation_Number"] == run]
        for NCLO in range(0, NCLO_max, NCLO_jumps):
            number_lines = len(df_per_run[(df_per_run['End_time'] < NCLO)])
            if NCLO not in nclo_dict:
                nclo_dict[NCLO] = []
            nclo_dict[NCLO].append(number_lines)
    return nclo_dict

def create_amount_delay_lines_dict(unique_num_runs, df, field_name):
    ans_dict = {}
    for run in unique_num_runs:
        df_per_run = df[df["Simulation_Number"] == run]
        num_lines_with_zero_penalty = len(df_per_run[df_per_run['Delay Penalty'] != 0])
        delay_sum = sum (df_per_run[df_per_run['Delay Penalty'] != 0]["Arrival Delay"])
        try:
            ans_dict[run] = delay_sum/num_lines_with_zero_penalty
        except:
            ans_dict[run]  = 0
    return statistics.mean(ans_dict.values())
