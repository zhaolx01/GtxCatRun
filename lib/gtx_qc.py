
import os,sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from lib.tools import check_file
from lib.linux_cmd import cmd_run
from lib.config import TestConfig
con=TestConfig()
gtx_all_path=con.get_soft("gtx_version_path")
ref=con.get_ref("gtx_index")

class GatkQc():
    def __init__(self,gtx,sample,bam,output_path):
        self.gtx=gtx
        self.output_path = output_path
        self.sample=sample
        self.bam =bam


    def CollectAlignmentSummaryMetrics(self):
        output = os.path.join(self.output_path, f'''{self.sample}_CollectAlignmentSummaryMetrics''')
        if check_file(f'{output}.txt'):
            return True
        else:
            if check_file(self.bam):
                cmd = f'''{self.gtx} qc --metrics CollectAlignmentSummaryMetrics -i {self.bam} -r {ref} -o {output}.txt'''
                with open(f'{self.output_path}/gtx_run.sh','a') as fp:
                    fp.writelines(cmd+'\n\n')
                return cmd_run(cmd,f'{output}.log')
            else:
                print('the file no exist:', self.bam)



    def CollectBaseDistributionByCycle(self):
        output = os.path.join(self.output_path, f'''{self.sample}_CollectBaseDistributionByCycle''')
        if check_file(f'{output}.pdf'):
            return True
        else:
            if check_file(self.bam):

                cmd=f'''{self.gtx} qc --metrics CollectBaseDistributionByCycle -i {self.bam} -o {output}.txt'''
                with open(f'{self.output_path}/gtx_run.sh','a') as fp:
                    fp.writelines(cmd+'\n\n')
                return cmd_run(cmd,f'{output}.log')
            else:
                print('the file no exist:', self.bam)


    def CollectGcBiasMetrics(self):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_CollectGcBiasMetrics''')
            cmd=f'''{self.gtx} qc --metrics CollectGcBiasMetrics -i {self.bam} -o {output}.txt -r {ref} -s {output}.summary_metrics.txt'''
            with open(f'{self.output_path}/gtx_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)


    def CollectInsertSizeMetrics(self):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_CollectInsertSizeMetrics''')
            cmd=f'''{self.gtx} qc --metrics CollectInsertSizeMetrics -i {self.bam} -o {output}.txt '''
            with open(f'{self.output_path}/gtx_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)
    def CollectQualityYieldMetrics(self):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_CollectQualityYieldMetrics''')
            cmd=f'''{self.gtx} qc --metrics CollectQualityYieldMetrics -i {self.bam} -o {output}.txt'''
            with open(f'{self.output_path}/gtx_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)


    def MeanQualityByCycle(self):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_MeanQualityByCycle''')
            cmd=f'''{self.gtx} qc --metrics MeanQualityByCycle -i {self.bam} -o {output}.txt'''
            with open(f'{self.output_path}/gatk_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)


    def QualityScoreDistribution(self):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_QualityScoreDistribution''')
            cmd=f'''{self.gtx} qc --metrics QualityScoreDistribution -i {self.bam} -o {output}.txt'''
            with open(f'{self.output_path}/gtx_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)

    def CollectHsMetrics(self,bait,call_bed):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_CollectHsMetrics''')
            cmd=f'''{self.gtx} qc --metrics CollectHsMetrics -i {self.bam} -o {output}.txt --bait_intervals {bait} --target_intervals {call_bed}'''
            with open(f'{self.output_path}/gtx_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)

    def CollectSequencingArtifactMetrics(self):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_CollectSequencingArtifactMetrics''')
            cmd = f'''{self.gtx} qc --metrics CollectSequencingArtifactMetrics -i {self.bam} -r {ref} -o {output}.txt'''
            with open(f'{self.output_path}/gtx_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)
    def CollectTargetedPcrMetrics(self,bait,call_bed):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_CollectTargetedPcrMetrics''')
            cmd=f'''{self.gtx} qc --metrics CollectTargetedPcrMetrics -i {self.bam} -o {output}.txt --amplicon_intervals {bait} --target_intervals {call_bed}'''
            with open(f'{self.output_path}/gtx_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)








if __name__ == '__main__':
    pass
