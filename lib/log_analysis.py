import os,sys,argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

'''
对输入目录下的*log文件时间排序后，抓取需要部分，追加放入xls中
'''
import csv


def file_name_walk(file_dir,suffix):
    output_list = [name for name in os.listdir(file_dir) if name.endswith(suffix)]
    #print(output_list)
    if len(output_list)==1:
        return os.path.join(log_path,output_list[0])

def get_time(file):

    with open(file,'r') as fp:
        datalines=fp.readlines()
        run_time=[i.strip().split('m:ss): ')[-1] for i in datalines if 'Elapsed (wall clock) time (h:mm:ss or m:ss):' in i]
        if len(run_time)==1:
            return run_time[0]
        else:
            print(run_time,'ERROR!!')

def analysis_log(log_path):
    csv_headr=['log path','Mutect2','normal.GetPileupSummaries','tumor.GetPileupSummaries','CalculateContamination','LearnReadOrientationModel','FilterMutectCalls']
    log_list=[file_name_walk(log_path,f'{i}.log') for i in csv_headr[1:]]
    row=[get_time(f) for f in log_list]
    row.insert(0,log_path)
    print(row)
    with open('log_analysis.csv', 'a', newline='', encoding='utf-8') as f:
        f_csv = csv.writer(f ,delimiter=',')
        f_csv.writerow(csv_headr)
        f_csv.writerow(row)





if __name__ == '__main__':
    log_path_list=['/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wes/FFX_IL_N_24h_2-FFX_IL_T_24h_1/gtx_2.0.1-pre2',
                   '/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wes/FFX_IL_N_24h_2-FFX_IL_T_24h_1/gatk_4.1.8.1',
                   '/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wgs/HCC1187BL-HCC1187C/gtx_2.0.1-pre2',
                   '/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wgs/HCC1187BL-HCC1187C/gatk_4.1.8.1'
                   ]

    #analysis_log(log_path)
    #file_name_walk(log_path, 'log')
    for log_path in log_path_list:
        analysis_log(log_path)