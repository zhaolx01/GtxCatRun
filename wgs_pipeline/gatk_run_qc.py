# -*- coding: utf-8 -*-

import os,sys,argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from lib.config import TestConfig
from lib.gatk_qc import GatkQc






con=TestConfig()
GATK_all_path=con.get_soft("gatk_verison_path")
#gatk,sample,bam,output_path
def run_gatk_qc(sample,bait,call_bed,VERSION='4.1.8.1'):
    if call_bed:
        #gtx_reference_data/analysis/germline/wes/HG001/gatk_4.1.8.1/HG001.sort.dup.bqsr.bam
        bam=os.path.join(con.get_analysis("wes_output_path"),f'{sample}/gatk_{VERSION}/{sample}.sort.dup.bqsr.bam')
        output_dir=os.path.join(con.get_analysis("wes_output_path"),f'{sample}/gatk_{VERSION}')
        print(os.path.join(con.get_analysis("wes_output_path")))
        print("----sample name:",sample)
        output_path=os.path.join(con.get_analysis("wes_output_path"),f"{sample}/gatk_{VERSION}")
        bait=os.path.join(con.get_data("wes_data"),bait)
        call_bed=os.path.join(con.get_data("wes_data"),call_bed)
    else:
        print('遇到再补充代码')
        return False
    gatk = f'java -jar '+os.path.join(f'{GATK_all_path}',f'gatk-package-{VERSION}-SNAPSHOT-local.jar')
    qc=GatkQc(gatk,sample,bam,output_path)
    print("----output path:", output_path)


    if qc.CollectAlignmentSummaryMetrics():
        if qc.CollectBaseDistributionByCycle():
            if qc.CollectGcBiasMetrics():
                if qc.CollectInsertSizeMetrics():
                    if qc.CollectQualityYieldMetrics():
                        if qc.MeanQualityByCycle():
                            if qc.QualityScoreDistribution():
                                if qc.CollectHsMetrics(bait=bait,call_bed=call_bed):
                                    if qc.CollectSequencingArtifactMetrics():
                                        if qc.CollectTargetedPcrMetrics(bait=bait,call_bed=call_bed):
                                            print('qc over')
                                        else:
                                            print('CollectTargetedPcrMetrics ERROR!!')
                                    else:
                                        print('CollectSequencingArtifactMetrics ERROR!!')
                                else:
                                    print('CollectHsMetrics ERROR!!')
                            else:
                                print('QualityScoreDistribution ERROR!!')
                        else:
                            print('MeanQualityByCycle ERROR!!')
                    else:
                        print('CollectQualityYieldMetrics ERROR!!')
                else:
                    print(f'CollectInsertSizeMetrics ERROR!!')
            else:
                print(f'CollectGcBiasMetrics ERROR!!')
        else:
            print('CollectBaseDistributionByCycle ERROR!!')
    else:
        print('CollectAlignmentSummaryMetrics ERROR!!')

# def arguments():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("sample",type=str,help="sample name")
#     parser.add_argument("fq1_gz", type=str, help="fq.gz read1")
#     parser.add_argument('--gatk_version',type=str,default='4.1.8.1')
#     parser.add_argument("-bed", type=str, default='')
#
#     args = parser.parse_args()
#     return args
#
# def run():
#     args=arguments()
#     sample=args.sample
#     fq_gz=args.fq1_gz
#     bed=args.bed
#     version=args.gatk_version
#     #print(sample,fq_gz,bed)
#     run_gatk_call_vcf(sample, fq_gz, bed=bed, VERSION=version)

if __name__=="__main__":
    run_gatk_qc('HG001', bait='S31285117_MergedProbes.interval_list', call_bed='S31285117_Regions_hg38.interval_list', VERSION='4.1.8.1')
    #run()