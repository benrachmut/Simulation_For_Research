import os
import pandas as pd
import statistics

import matplotlib.pyplot as plt

NCLO_jumps = 10000
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

folder_path = r'C:\Users\Ben\Desktop\CADCOP data II\v18 journal fisher'  # Replace with the path to your folder
raw_task_data = pd.read_csv(folder_path+"\\"+"Task_raw_data.csv")
folder_path = r'C:\Users\Ben\Desktop\dynamic'  # Replace with the path to your folder

#print(raw_task_data.columns.values)

# Get all the files in the folder
folder_names = os.listdir(folder_path)



# Iterate over the files and print their names
for folder_name in folder_names:
    temp_path1 = folder_path+"\\"+folder_name
    folders_of_excel_files1 = os.listdir(temp_path1)
    lines = ["Protocol,Algorithm,NCLO,Average"]


    for folder_of_excel_file1 in folders_of_excel_files1:
        temp_path2 = temp_path1 + "\\" + folder_of_excel_file1

        folders_of_excel_files2 = os.listdir(temp_path1)

        excel_names = os.listdir(temp_path2)

        df = concatenate_csv_lines(excel_names,temp_path2)

        df = pd.merge(df, raw_task_data, on=['Task Id','Simulation_Number'])

        df["End_time"] = df["Arrival_time"] + df["Total Time In System"]

        max_end_time = max(df["End_time"])

        unique_num_runs = pd.unique(df["Simulation_Number"])
        nclo_dict = {}

        for run in unique_num_runs:
            df_per_run = df[df["Simulation_Number"] == run]
            for NCLO in range(0, 5000000,NCLO_jumps):
                relevant_lines_per_nclo = []
                selected_rows = df[(df['End_time'] < NCLO)]['Utility']
                sum_per_NCLO = sum(selected_rows.tolist())
                if NCLO not in nclo_dict:
                    nclo_dict[NCLO] = []
                nclo_dict[NCLO].append(sum_per_NCLO)

        avg_per_nclo = {}
        for nclo, all_results in nclo_dict.items():
            avg_per_nclo[nclo] = statistics.mean(all_results)


        for nclo, avg in avg_per_nclo.items():
            comm = folder_name
            algo = folder_of_excel_file1
            line = comm+","+algo+","+ str(nclo)+","+str(avg)
            lines.append(line)
    df = pd.DataFrame(lines, columns=['String'])
    # Create Excel file
    print(folder_name)
    df.to_csv(folder_name+".csv", index=False)