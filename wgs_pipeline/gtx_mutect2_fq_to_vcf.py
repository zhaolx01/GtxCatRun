import os,sys,argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from lib.config import TestConfig
from wgs_pipeline.gtx_fq_to_vcf import run_gtx_call_vcf
from lib.gtx_mutect2 import GtxMutect2


con=TestConfig()
gtx_all_path=con.get_soft("gtx_version_path")
ref=con.get_ref("gtx_index")

def run_gtx_mutect2(normal_sample,tumor_sample,normal_fq_r1,tumor_fq_r1,bed='',VERSION='2.0.1-pre2'):
    if bed:
        output_path=os.path.join(con.get_analysis("wes_mutect2_output_path"),f"{normal_sample}-{tumor_sample}/gtx_{VERSION}")
        bed=os.path.join(con.get_data("wes_mutect2_data"),bed)
        normal_bam = os.path.join(con.get_analysis("wes_mutect2_output_path"),
                                  f"{normal_sample}/gtx_{VERSION}/{normal_sample}.sort.dup.bqsr.bam")
        tumor_bam = os.path.join(con.get_analysis("wes_mutect2_output_path"),
                                 f"{tumor_sample}/gtx_{VERSION}/{tumor_sample}.sort.dup.bqsr.bam")
    else:
        output_path = os.path.join(con.get_analysis("wgs_mutect2_output_path"),f"{normal_sample}-{tumor_sample}/gtx_{VERSION}")
        normal_bam = os.path.join(con.get_analysis("wgs_mutect2_output_path"), f"{normal_sample}/gtx_{VERSION}/{normal_sample}.sort.dup.bqsr.bam")
        tumor_bam=os.path.join(con.get_analysis("wgs_mutect2_output_path"), f"{tumor_sample}/gtx_{VERSION}/{tumor_sample}.sort.dup.bqsr.bam")
    print("----sample name:", normal_sample, tumor_sample)
    print("----output path:", output_path)
    gtx = os.path.join(gtx_all_path, f'{VERSION}/gtx')
    #print('@@@@@@@@@@@',gtx)
    #将normal 与tumor的fq做全流程得出.sort.dup.bqsr.bam
    os.makedirs(output_path, exist_ok=True)

    if run_gtx_call_vcf(normal_sample,normal_fq_r1,bed=bed,site='call_mutect2',VERSION=VERSION):
        #print('11111111111111111')
        if run_gtx_call_vcf(tumor_sample,tumor_fq_r1,bed=bed,site='call_mutect2',VERSION=VERSION):
            #print('222222222222')
            #跑mutect2剩下流程
            gtx_run=GtxMutect2(output_path,normal_sample,tumor_sample,normal_bam,tumor_bam,gtx,bed=bed)
            if gtx_run.Mutect2():
                if gtx_run.Gps_tumor():
                    if gtx_run.Gps_normal():
                        if gtx_run.Calc():
                            if gtx_run.Learn():
                                if gtx_run.Filter():
                                    print('----mutect2 run over')
                                else:
                                    print('Filter ERROR!!')
                            else:
                                print('Learn ERROR!!')
                        else:
                            print('Calc ERROR!!')
                    else:
                        print('Gps_normal ERROR!!')
                else:
                    print('Gpss_tumor ERROR!!')
            else:
                print('Mutect2 ERROR!!')
        else:
            print('run_gtx_call_vcf tumor ERROR！！')
    else:
        print('run_gtx_call_vcf normal ERROR！！')












if __name__=='__main__':
    l=['FFX_IL_N_24h_2','FFX_IL_T_24h_1','SRR7890951_1.fastq.gz','SRR7890933_1.fastq.gz','Agilent_Human_Exon_V6_UTRs_Regions.interval_list']
    run_gtx_mutect2(*l,VERSION='2.0.1-pre2')
