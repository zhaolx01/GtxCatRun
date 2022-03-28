# -*- coding: utf-8 -*-
#所有路径转为绝对路径，
#对应目录结构获取数据与生成数据及日志
#分化为基础步骤的各个脚本
#思考数据引用路径问题
import os,sys,argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from lib.config import TestConfig
from lib.gatk_step import GatkStep






con=TestConfig()
GATK_all_path=con.get_soft("gatk_verison_path")

def run_gatk_call_vcf(sample,fq_gz,bed='',VERSION='4.1.8.1',site='call_vcf',CPU=72,is_clear=True):
    if bed and site=='call_vcf':
        fq_gz=os.path.join(con.get_data("wes_data"),fq_gz)
        output_path=os.path.join(con.get_analysis("wes_output_path"),f"{sample}/gatk_{VERSION}")
        bed=os.path.join(con.get_data("wes_data"),bed)
    elif bed=='' and site=='call_vcf':
        fq_gz = os.path.join(con.get_data("wgs_data"), fq_gz)
        output_path = os.path.join(con.get_analysis("wgs_output_path"), f'{sample}/gatk_{VERSION}')

    elif bed and site=='call_mutect2':
        #print('---------1')
        fq_gz = os.path.join(con.get_data("wes_mutect2_data"), fq_gz)
        output_path = os.path.join(con.get_analysis("wes_mutect2_output_path"), f"{sample}/gatk_{VERSION}")
        bed = os.path.join(con.get_data("wes_mutect2_data"), bed)
    elif bed=='' and site=='call_mutect2':
        #print('---------2')
        fq_gz = os.path.join(con.get_data("wgs_mutect2_data"), fq_gz)
        output_path = os.path.join(con.get_analysis("wgs_mutect2_output_path"), f"{sample}/gatk_{VERSION}")
    else:
        print('site error!!')
    if output_path:
        gatk = f'java -jar '+os.path.join(f'{GATK_all_path}',f'gatk-package-{VERSION}-SNAPSHOT-local.jar')
        gatk_run = GatkStep(sample,output_path,CPU)
        os.makedirs(output_path, exist_ok=True)
        #print(os.path.join(con.get_analysis("wes_output_path")))
        print("----sample name:", sample)
        print("----output path:", output_path)
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

        if gatk_run.align_sort(r1,r2):
            if gatk_run.Gatk_MarkDuplicates(gatk):
                if gatk_run.Gatk_bqsr(gatk):
                    if site=='call_mutect2':
                        if is_clear:
                            os.system(
                                f'rm {output_path}/{sample}.sort.bam* {output_path}/{sample}.sort.dup.bam* {output_path}/{sample}.dup.out {output_path}/{sample}.bqsr.grp')
                        return True

                    else:
                        if gatk_run.Gatk_HaplotypeCaller(gatk,bed):

                            return True
                        else:
                            print(f'Gatk_HaplotypeCaller ERROR!!')
            else:
                print('Gatk_MarkDuplicates ERROR!!')
        else:
            print('align ERROR!!')

def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("sample",type=str,help="sample name")
    parser.add_argument("fq1_gz", type=str, help="fq.gz read1")
    parser.add_argument('--gatk_version',type=str,default='4.1.8.1')
    parser.add_argument("-bed", type=str, default='')

    args = parser.parse_args()
    return args

def run():
    args=arguments()
    sample=args.sample
    fq_gz=args.fq1_gz
    bed=args.bed
    version=args.gatk_version
    #print(sample,fq_gz,bed)
    run_gatk_call_vcf(sample, fq_gz, bed=bed, VERSION=version)

if __name__=="__main__":

    run_gatk_call_vcf('HG001','SRR14724483_1.fastq.gz',bed='S31285117_Regions_hg38.interval_list', VERSION='4.1.8.1')
    #run()