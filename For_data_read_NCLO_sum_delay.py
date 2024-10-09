import os
import pandas as pd
import statistics


from For_data_read_Glob import *

field_name ="Arrival Delay"
#print(raw_task_data.columns.values)

# Get all the files in the folder
folder_names = ["u100k"]#os.listdir(folder_path)
# Iterate over the files and print their names
for folder_name in folder_names:
    temp_path1 = folder_path+"\\"+folder_name
    folders_of_excel_files1 = os.listdir(temp_path1)
    #folders_of_excel_files1 = ["asy","sy_05"]

    #lines = ["Protocol,Algorithm,NCLO,Average"]
    lines = []

    for folder_of_excel_file1 in folders_of_excel_files1:
        temp_path2 = temp_path1 + "\\" + folder_of_excel_file1

        folders_of_excel_files2 = os.listdir(temp_path1)
        excel_names = os.listdir(temp_path2)

        df = concatenate_csv_lines(excel_names,temp_path2)
        df = pd.merge(df, raw_task_data, on=['Task Id','Simulation_Number'])
        df = df.drop_duplicates(subset=['Task Id','Simulation_Number',"Mission Id"])

        df['Arrival Delay'] = df.apply(
            lambda row: NCLO_max - row['Arrival_time'] if pd.isnull(row['Arrival Delay']) else row['Arrival Delay'],
            axis=1)

        #df["Total Time In System"] = df.apply(
        #    lambda row: df['Arrival Delay'] if pd.isnull(row["Total Time In System"]) else row["Total Time In System"],
        #    axis=1)
        df['Total Time In System'] = df['Total Time In System'].fillna(df['Arrival Delay'])

        df["End_time"] = df["Arrival_time"] + df["Total Time In System"]

        df["Time_of_First_Arrive"] = df["Arrival_time"] + df["Arrival Delay"]

        ##max_end_time = max(df["End_time"])
        unique_num_runs = pd.unique(df["Simulation_Number"])
        nclo_dict = create_nclo_dict_for_updated_delay(unique_num_runs,df,field_name=field_name)
        avg_per_nclo = {}
        for nclo, all_results in nclo_dict.items():
            avg_per_nclo[nclo] = statistics.mean(all_results)


        for nclo, avg in avg_per_nclo.items():
            comm = folder_name
            algo = folder_of_excel_file1
            line = [comm , algo ,nclo,avg]
            lines.append(line)

        print(folder_of_excel_file1)
    df = pd.DataFrame(lines, columns=['Protocol', 'Algorithm', 'NCLO', "Average"])
    #df = df.drop(0)
    #df[0] = df[0].str.split(', ', expand=True)
    #df[["Protocol","Algorithm","NCLO","Average"]] = df[0].str.split(', ', expand=True)

    # Create Excel file
    print("---------"+folder_name+"---------")
    df.to_csv(folder_name + field_name+".csv", index=False)

