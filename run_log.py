import os,sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import argparse
from lib import log_analysis

wes_log=['/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/germline/wes/HG001/gatk_4.1.8.1','/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/germline/wes/HG001/gtx_2.1.0-pre1']
wgs=["HG001","HG002","HG003", "HG004"]
wgs_path='/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/germline/wgs/'
#formats = [f'{wgs_path}{}/gatk_4.1.8.1', f'{wgs_path}{}/gtx_2.1.0-pre1']
formats = ['/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/germline/wgs/{}/gatk_4.1.8.1','/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/germline/wgs/{}/gtx_2.1.0-pre1']
wgs_log= [f.format(x) for f in formats for x in wgs]

wes_mutect2=['FFX_IL_N_24h_2','FFX_IL_T_24h_1','FFX_IL_N_24h_2-FFX_IL_T_24h_1']
wes_mutect2_path='/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wes/'
#formats= [f'{wes_mutect2_path}{}/gatk_4.1.8.1', f'{wes_mutect2_path}{}/gtx_2.1.0-pre1']
formats= ['/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wes/{}/gatk_4.1.8.1','/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wes/{}/gtx_2.1.0-pre1']
wes_mutect2_log=[f.format(x) for f in formats for x in wes_mutect2]


wgs_mutect2=['HCC1187BL', 'HCC1187C', 'HCC1187BL-HCC1187C']
wgs_mutect2_path='/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wgs/'
#formats= [f'{wgs_mutect2_path}{}/gatk_4.1.8.1', f'{wgs_mutect2_path}{}/gtx_2.1.0-pre1']
formats = ['/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wgs/{}/gatk_4.1.8.1','/ssd-cache/zlx/gtx-run/gtx_reference_data/analysis/somatic/wgs/{}/gtx_2.1.0-pre1']
wgs_mutect2_log=[f.format(x) for f in formats for x in wgs_mutect2]







def run_log_analysis(log_site,info_site):
        
    if log_site=='wgs_log':
        log_path_list=wgs_log
        run_site='wgs'
    elif log_site=='wes_log':
        log_path_list=wes_log
        run_site='wgs'
    elif log_site=='wgs_mutect2_log':
        log_path_list=wgs_mutect2_log
        run_site='wgs_mutect2'
    elif log_site=='wes_mutect2_log':
        log_path_list=wes_mutect2_log
        run_site='wgs_mutect2'
    
    else:
        print('log site error!')


    if log_path_list:
        log_analysis.run_analysis(log_path_list,info_site)


if __name__ == '__main__':
    # run_log_analysis('wes_mutect2_log','wgs_mutect2')
    # run_log_analysis('wgs_mutect2_log', 'wgs_mutect2')
    run_log_analysis('wes_log', 'wgs')
    run_log_analysis('wgs_log', 'wgs')

