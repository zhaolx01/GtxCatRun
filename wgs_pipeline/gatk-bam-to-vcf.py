
import os,sys
from lib.config import TestConfig
from lib.gatk_step import GatkStep

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)



con=TestConfig()
GATK_all_path=con.get_soft("gatk_verison_path")

def run_gatk_bam_to_vcf(sample,bed='',VERSION='4.1.7.0',CPU=72):
    if bed:
        output_path=os.path.join(con.get_analysis("wes_output_path"),f'{sample}/gatk_{VERSION}')
        bed = os.path.join(con.get_data("wes_data"), bed)
    else:
        output_path = os.path.join(con.get_analysis("wgs_output_path"), '{sample}/gatk_{VERSION}')
    gatk = f'java -jar {GATK_all_path}/gatk-package-{VERSION}-SNAPSHOT-local.jar'
    gatk_run = GatkStep(sample,output_path,CPU)
    os.makedirs(output_path, exist_ok=True)
    print("output path:", output_path)

    if gatk_run.Gatk_HaplotypeCaller(gatk,bed):
        return True
    else:
        print('Gatk_MarkDuplicates ERROR!!')



if __name__=="__main__":
    run_gatk_bam_to_vcf('HG001','S31285117_Regions_hg38.bed',VERSION='4.1.7.0')