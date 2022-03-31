import os,sys,argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

'''
对输入目录下的*log文件时间排序后，抓取需要部分，追加放入xls中
'''
import csv,time


def file_name_walk(file_dir,suffix):
    output_list = [name for name in os.listdir(file_dir) if name.endswith(suffix)]
    #print(output_list)
    if len(output_list)==1:
        return os.path.join(file_dir,output_list[0])

def get_time(file):
    try:
        with open(file,'r') as fp:
            datalines=fp.readlines()
            run_time=[i.strip().split('m:ss): ')[-1] for i in datalines if 'Elapsed (wall clock) time (h:mm:ss or m:ss):' in i]
            if len(run_time)==1:
                return run_time[0]
            else:
                print('get time ERROR!!')
    except Exception as err:
        print(file,err)

def get_cpu(file):
    try:
        print(file,'!!!!!!!!!')
        with open(file,'r') as fp:
            datalines=fp.readlines()
            run_cpu=[i.strip().split('CPU this job got: ')[-1] for i in datalines if 'Percent of CPU this job got:' in i]
            if len(run_cpu)==1:
                return run_cpu[0]
            else:
                print('get CPU ERROR!!')
    except Exception as err:
        print(file, '!!!!!!!!!')
        print(file, err)

def get_mem(file):
    try:
        with open(file,'r') as fp:
            datalines=fp.readlines()
            run_mem=[i.strip().split('Maximum resident set size (kbytes): ')[-1] for i in datalines if 'Maximum resident set size (kbytes):' in i]
            if len(run_mem)==1:
                return run_mem[0]
            else:
                print('get CPU ERROR!!')
    except Exception as err:
        print(file, err)

def analysis_log(log_path_list,info_list,info_site='run_time'):
    csv_headers = ['process', 'site', 'sample', 'version'] + info_list
    localtime = time.asctime(time.localtime(time.time()))
    print(f'get_{info_site}.csv')
    with open(f'get_{info_site}.csv', 'a') as f:
        f_csv = csv.writer(f)
        f_csv.writerow([localtime])
        f_csv.writerow(csv_headers)
        for log_path in log_path_list:
            log_list = [file_name_walk(log_path, f'{i}.log') for i in info_list]
            if info_site == 'run_cpu':
                row = [get_cpu(file) for file in log_list]

            elif info_site == 'run_mem':
                row = [get_mem(file) for file in log_list]
            else:
                row = [get_time(file) for file in log_list]
            *_, process, site, sample, version = log_path.strip().split('/')
            row = [process, site, sample, version] + row
            print(row)
            f_csv.writerow(row)



def gatk_analysis_log(log_path_list,run_site='wgs_mutect2',):
    wgs_info = ['align.sort', 'sort.bam.index', 'dup', 'dup.bam.index', 'BaseRecalibrator', 'ApplyBQSR',
                'HaplotypeCaller']
    mutect2_info = ['Mutect2', 'normal.GetPileupSummaries', 'tumor.GetPileupSummaries', 'CalculateContamination',
                    'LearnReadOrientationModel', 'FilterMutectCalls']
    wgs_mutect2_info=wgs_info+mutect2_info
    del wgs_mutect2_info[6]
    if run_site=='wgs':
        info_list=wgs_info
    elif run_site=='mutect2':
        info_list=mutect2_info
    elif run_site=='wgs_mutect2':
        info_list=wgs_mutect2_info
    else:
        print('run site error')
    analysis_log(log_path_list,info_list,run_site)


def gtx_analysis_log(log_path_list,run_site='wgs_mutect2'):
    wgs_info = ['gtx']
    mutect2_info = ['align', 'bqsr', 'Mutect2','normal.GetPileupSummaries','tumor.GetPileupSummaries', 'CalculateContamination',
                    'LearnReadOrientationModel', 'FilterMutectCalls']
    if run_site=='wgs':
        info_list=wgs_info
    elif run_site=='wgs_mutect2':
        info_list=mutect2_info
    else:
        print('run site error')
    analysis_log(log_path_list,info_list,run_site)
def run_analysis(log_path_list,run_site='wgs_mutect2'):
    gtx_log=[]
    gatk_log=[]
    print(log_path_list,'NNNNNNNNNNNNNNN')
    for log_path in log_path_list:
        if 'gatk' in log_path:
            gatk_log.append(log_path)
        elif 'gtx' in log_path:
            gtx_log.append(log_path)
    print(gtx_log,'@@@@@@@@@@@@@')
    if gtx_log:
       gtx_analysis_log(gtx_log,run_site=run_site)
    if gatk_log:
       gatk_analysis_log(gatk_log,run_site=run_site)


if __name__ == '__main__':
    #mutect2


    #call vcf
    # log_path_list=['/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/germline/wes/HG001/gatk_4.1.8.1',
    #                '/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/germline/wgs/HG001/gatk_4.1.8.1',
    #                '/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/germline/wgs/HG002/gatk_4.1.8.1',
    #                '/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/germline/wgs/HG003/gatk_4.1.8.1',
    #                '/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/germline/wgs/HG004/gatk_4.1.8.1',
    #                '/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wgs/HCC1187BL/gatk_4.1.8.1',
    #                '/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wgs/HCC1187C/gatk_4.1.8.1']
    #'/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wes/FFX_IL_N_24h_2-FFX_IL_T_24h_1_bak/gtx_2.0.1-pre2','/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wes/FFX_IL_N_24h_2-FFX_IL_T_24h_1_bak/gatk_4.1.8.1',
    gatk_log_path_list=['/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wgs/HCC1187BL/gatk_4.1.8.1',
                   '/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wgs/HCC1187C/gatk_4.1.8.1',
                   '/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wgs/HCC1187BL-HCC1187C/gatk_4.1.8.1',
                ]
    gatk_analysis_log(gatk_log_path_list)
    # gtx_log_path_list=[   '/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wgs/HCC1187BL/gtx_2.0.1-pre2',
    #                '/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wgs/HCC1187C/gatk_4.1.8.1/gtx_2.0.1-pre2',
    #                '/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wgs/HCC1187BL-HCC1187C/gtx_2.0.1-pre2'
    #                ]
