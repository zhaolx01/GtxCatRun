# -*- coding: utf-8 -*-
#所有路径转为绝对路径，
#对应目录结构获取数据与生成数据及日志
#分化为基础步骤的各个脚本
#思考数据引用路径问题
import os,sys,argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from lib.config import TestConfig
from lib.linux_cmd import cmd_run
from lib.gtx_step import GtxStep



con=TestConfig()
gtx_all_path=con.get_soft("gtx_version_path")
ref=con.get_ref("gtx_index")
known_Mills=con.get_knownsites_vcf("known_Mills")
known_1000G=con.get_knownsites_vcf("known_1000G")
known_dbsnp=con.get_knownsites_vcf("known_dbsnp")

def run_gtx_call_vcf(sample,fq_gz,bed='',site='call_vcf',is_keep_bam=False,VERSION='2.0.1-pre2'):
    #根据是否有bed判断wes、wgs,自动添加路径
    if bed and site=='call_vcf':
        fq_gz=os.path.join(con.get_data("wes_data"),fq_gz)
        output_path=os.path.join(con.get_analysis("wes_output_path"),f"{sample}/gtx_{VERSION}")
        bed=os.path.join(con.get_data("wes_data"),bed)
    elif bed == '' and site == 'call_vcf':
        fq_gz = os.path.join(con.get_data("wgs_data"), fq_gz)
        output_path = os.path.join(con.get_analysis("wgs_output_path"), f'{sample}/gtx_{VERSION}')
    elif bed and site == 'call_mutect2':
        fq_gz = os.path.join(con.get_data("wes_mutect2_data"), fq_gz)
        output_path = os.path.join(con.get_analysis("wes_mutect2_output_path"), f"{sample}/gtx_{VERSION}")
        bed = os.path.join(con.get_data("wes_mutect2_data"), bed)
    elif bed == '' and site == 'call_mutect2':
        fq_gz = os.path.join(con.get_data("wgs_mutect2_data"), fq_gz)
        output_path = os.path.join(con.get_analysis("wgs_mutect2_output_path"), f'{sample}/gtx_{VERSION}')
    else:
        print('site error!!')
    if output_path:
        print("----sample name:", sample)
        print("----output path:", output_path)
        os.makedirs(output_path, exist_ok=True)
        gtx = os.path.join(gtx_all_path,f'{VERSION}/gtx')
        r1 = fq_gz
        if '_1' in fq_gz:
            r2 = fq_gz.replace('_1', '_2')
        elif '.R1' in fq_gz:
            r2 = fq_gz.replace('.R1', '.R2')
        elif '_R1' in fq_gz:
            r2 = fq_gz.replace('_R1', '_R2')
        else:
            print('Fq Format error  ~~')
            return False
        gtx_run=GtxStep(sample,output_path,gtx)
        if site=='call_mutect2':
            if gtx_run.Align(r1,r2):
                if gtx_run.Bqsr():
                    print('make sort.dup.bqsr.bam over')
                    return True
                else:
                    print('bqsr ERROR!!')
            else:
                print('align ERROR!!')
        else:
            if gtx_run.Wgs(r1,r2,bed=bed,is_keep_bam=is_keep_bam):
                print('wgs over')
                return True
            else:
                print('wgs ERROR!!')



def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("sample",type=str,help="sample name",default='HG001')
    parser.add_argument("fq1_gz", type=str, help="fq.gz read1",default='SRR14724483_1.fastq.gz')
    parser.add_argument('--gtx_version',type=str,default='2.1.0-pre1',choices=['2.1.0-pre1','2.0.1-pre2'])
    parser.add_argument("-bed", type=str, default='S31285117_Regions_hg38.interval_list')

    args = parser.parse_args()
    return args

def run():
    args=arguments()
    sample=args.sample
    fq_gz=args.fq1_gz
    bed=args.bed
    version=args.gatk_version
    #print(sample,fq_gz,bed)
    run_gtx_call_vcf(sample, fq_gz, bed=bed, VERSION=version)

if __name__=="__main__":

    run_gtx_call_vcf('HG001','SRR14724483_1.fastq.gz',bed='S31285117_Regions_hg38.interval_list', VERSION='2.0.1-pre2')