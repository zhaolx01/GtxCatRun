
import os,sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from lib.config import TestConfig
from wgs_pipeline.gatk_fq_to_vcf import run_gatk_call_vcf
from lib.gatk_mutect2 import GatkMutect2

con=TestConfig()
GATK_all_path=con.get_soft("gatk_verison_path")

def run_gatk_mutect2(normal_sample,tumor_sample,normal_fq_r1,tumor_fq_r1,bed='',VERSION='4.1.8.1'):
    if bed:
        output_path=os.path.join(con.get_analysis("wes_mutect2_output_path"),f"{normal_sample}-{tumor_sample}/gatk_{VERSION}")
        bed=os.path.join(con.get_data("wes_mutect2_data"),bed)
        normal_bam = os.path.join(con.get_analysis("wes_mutect2_output_path"),
                                  f"{normal_sample}/gatk_{VERSION}/{normal_sample}.sort.dup.bqsr.bam")
        tumor_bam = os.path.join(con.get_analysis("wes_mutect2_output_path"),
                                 f"{tumor_sample}/gatk_{VERSION}/{tumor_sample}.sort.dup.bqsr.bam")
    else:
        output_path = os.path.join(con.get_analysis("wgs_mutect2_output_path"),f"{normal_sample}-{tumor_sample}/gatk_{VERSION}")
        normal_bam = os.path.join(con.get_analysis("wgs_mutect2_output_path"), f"{normal_sample}/gatk_{VERSION}/{normal_sample}.sort.dup.bqsr.bam")
        tumor_bam=os.path.join(con.get_analysis("wgs_mutect2_output_path"), f"{tumor_sample}/gatk_{VERSION}/{tumor_sample}.sort.dup.bqsr.bam")
    print("----sample name:", normal_sample, tumor_sample)
    print("----output path:", output_path)
    gatk = f'java -jar ' + os.path.join(f'{GATK_all_path}', f'gatk-package-{VERSION}-SNAPSHOT-local.jar')
    #将normal 与tumor的fq做全流程得出.sort.dup.bqsr.bam
    os.makedirs(output_path, exist_ok=True)
    if run_gatk_call_vcf(normal_sample,normal_fq_r1,bed=bed,VERSION=VERSION,site='call_mutect2',is_clear=False):
        if run_gatk_call_vcf(tumor_sample,tumor_fq_r1,bed=bed,VERSION=VERSION,site='call_mutect2',is_clear=False):
            #跑mutect2剩下流程
            gatk_run=GatkMutect2(output_path,normal_sample,tumor_sample,normal_bam,tumor_bam,gatk,bed=bed)
            if gatk_run.Mutect2():
                if gatk_run.GetPileupSummaries_tumor():
                    if gatk_run.GetPileupSummaries_normal():
                        if gatk_run.CalculateContamination():
                            if gatk_run.LearnReadOrientationModel():
                                if gatk_run.FilterMutectCalls():
                                    print('----mutect run over')
                                else:
                                    print('FilterMutectCalls ERROR!!')
                            else:
                                print('LearnReadOrientationModel ERROR!!')
                        else:
                            print('CalculateContamination ERROR!!')
                    else:
                        print('GetPileupSummaries_normal ERROR!!')
                else:
                    print('GetPileupSummaries_tumor ERROR!!')
            else:
                print('Mutect2 ERROR!!')
    else:
        print('run_gatk_call_vcf ERROR！！')





if __name__ == '__main__':
    l = ['HCC1187BL', 'HCC1187C', 'HCC1187BL_S1_L001_R1_001.fastq.gz', 'HCC1187C_S1_L001_R1_001.fastq.gz']
    run_gatk_mutect2(*l,VERSION='4.1.8.1')
