# -*- coding: utf-8 -*-
import os,sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import argparse
from wgs_pipeline.gatk_fq_to_vcf import run_gatk_call_vcf
from wgs_pipeline.gtx_fq_to_vcf import run_gtx_call_vcf
from wgs_pipeline.compare import Happy_vs
from wgs_pipeline.gatk_mutect2_fq_to_vcf import run_gatk_mutect2
from wgs_pipeline.gtx_mutect2_fq_to_vcf import run_gtx_mutect2
from lib.log_analysis import *


gatk_version='4.1.8.1'
gtx_version='2.1.0-pre1'

wgs_sample_dict=[{"sample":"HG001_wes","test_data":["HG001","SRR14724483_1.fastq.gz","S31285117_Regions_hg38.bed"]},
                 {"sample": "HG001",
                  "test_data": ["HG001", "140127_D00360_0011_AHGV6ADXX_R1.fastq.gz"]},
                 {"sample": "HG002",
                  "test_data": ["HG002", "HG002.novaseq.pcr-free.35x.R1.fastq.gz"]},
                 {"sample": "HG003",
                  "test_data": ["HG003", "HG003.novaseq.pcr-free.35x.R1.fastq.gz"]},
                 {"sample": "HG004",
                  "test_data": ["HG004", "HG004.novaseq.pcr-free.35x.R1.fastq.gz"]},
                 ]

mutect2_sample_dict=[{"tumor_sample":"HCC1187C","normal_sample":"HCC1187BL",
                      "test_data":['HCC1187BL', 'HCC1187C', 'HCC1187BL_S1_L001_R1_001.fastq.gz', 'HCC1187C_S1_L001_R1_001.fastq.gz']},
                 {"tumor_sample": "FFX_IL_T_24h_1","normal_sample":"FFX_IL_N_24h_2",
                  "test_data": ['FFX_IL_N_24h_2','FFX_IL_T_24h_1','SRR7890951_1.fastq.gz','SRR7890933_1.fastq.gz','Agilent_Human_Exon_V6_UTRs_Regions.interval_list']},
                 ]

def run_wgs(sample,site,version):
    if version:
        test_data=[i["test_data"] for i in wgs_sample_dict if i["sample"]==sample][0]
        print(test_data)
        if site=='gtx_wgs':
            run_gtx_call_vcf(*test_data, VERSION=version)
        elif site=='gatk_wgs':
            run_gatk_call_vcf(*test_data,VERSION=version)
    else:
        print('请指定--version')


def run_mutect2(sample,site,version):
    if version:
        test_data=[i["test_data"] for i in mutect2_sample_dict if i["tumor_sample"]==sample or i["normal_sample"]==sample][0]
        #print(test_data)
        if site=='gatk_mutect2':
            run_gatk_mutect2(*test_data, VERSION=version)
        elif site=='gtx_mutect2':
            print('run gtx mutect2.........')
            run_gtx_mutect2(*test_data,VERSION=version)
    else:
        print('请指定--version')

def run_vcf_pk(sample,site,gtx_version,gatk_version):

    if site=='pk_wgs':
        test_data=[i["test_data"] for i in wgs_sample_dict if i["sample"]==sample][0]
    #比较
        sample=test_data[0]
        happy=Happy_vs(sample)
        if len(test_data)==3:
            #happy.benchmark_vs_gatk(gatk_version,call_bed=inf[2])
            happy.gatk_vs_gtx(gatk_version,gtx_version,call_bed=test_data[2])
            happy.benchmark_vs_gtx(gtx_version,call_bed=test_data[2])
        else:
            #happy.benchmark_vs_gatk(gatk_version)
            happy.gatk_vs_gtx(gatk_version, gtx_version)
            happy.benchmark_vs_gtx(gtx_version)
    elif site=='pk_mutect2':
        test_data=[i["test_data"] for i in mutect2_sample_dict if i["tumor_sample"]==sample or i["normal_sample"]==sample][0]
        happy = Happy_vs(test_data[0])
        if len(test_data)==5:
            happy.gatk_vs_gtx_mutect2(gatk_version, gtx_version, test_data[0],test_data[1],test_data[-1])
        else:
            happy.gatk_vs_gtx_mutect2(gatk_version, gtx_version, *test_data[:2])





def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("sample",type=str,help="sample name")
    parser.add_argument("site", type=str, help="run site",choices=['gtx_wgs','gatk_wgs','gtx_mutect2','gatk_mutect2','pk_wgs','pk_mutect2'])
    parser.add_argument('--gatk_version',type=str,default='4.1.8.1')
    parser.add_argument('--gtx_version',type=str,default='2.1.0-pre1')
    parser.add_argument('--version', type=str, help='用于进行全流程或者mutect2计算的gatk版本或者gtx版本',default=["2.1.0-pre1",'4.1.8.1'])
    args = parser.parse_args()
    return args

def run():
    args=arguments()
    sample=args.sample
    site=args.site
    gatk_version=args.gatk_version
    gtx_version=args.gtx_version
    version=args.version
    print(sample,site,version)
    if site in ['gtx_wgs','gatk_wgs']:

        run_wgs(sample,site,version)
    elif site in ['gtx_mutect2','gatk_mutect2']:

        run_mutect2(sample,site,version)
    elif site in ['pk_wgs','pk_mutect2']:

        run_vcf_pk(sample,site,gtx_version,gatk_version)
    else:
        print('site error!!')


if __name__=="__main__":
    run()