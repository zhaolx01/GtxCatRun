
import os,sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from lib.tools import check_file
from lib.linux_cmd import cmd_run
from lib.config import TestConfig
con=TestConfig()
ref=con.get_ref("bwa_index")

class GatkQc():
    def __init__(self,gatk,sample,bam,output_path):
        self.gatk=gatk
        self.output_path = output_path
        self.sample=sample
        self.bam =bam


    def CollectAlignmentSummaryMetrics(self):
        output = os.path.join(self.output_path, f'''{self.sample}_CollectAlignmentSummaryMetrics''')
        if check_file(f'{output}.txt'):
            return True
        else:
            if check_file(self.bam):

                cmd = f'''{self.gatk} CollectAlignmentSummaryMetrics -I {self.bam} -R {ref} -O  {output}.txt'''
                with open(f'{self.output_path}/gatk_run.sh','a') as fp:
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

                cmd=f'''{self.gatk} CollectBaseDistributionByCycle -I {self.bam} -O {output}.txt -CHART {output}.pdf'''
                with open(f'{self.output_path}/gatk_run.sh','a') as fp:
                    fp.writelines(cmd+'\n\n')
                return cmd_run(cmd,f'{output}.log')
            else:
                print('the file no exist:', self.bam)


    def CollectGcBiasMetrics(self):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_CollectGcBiasMetrics''')
            cmd=f'''{self.gatk} CollectGcBiasMetrics -I {self.bam} -O {output}.txt -R {ref} -S {output}.summary_metrics.txt -CHART {output}.pdf'''
            with open(f'{self.output_path}/gatk_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)


    def CollectInsertSizeMetrics(self):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_CollectInsertSizeMetrics''')
            cmd=f'''{self.gatk} CollectInsertSizeMetrics -I {self.bam} -O {output}.txt -H {output}.pdf'''
            with open(f'{self.output_path}/gatk_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)
    def CollectQualityYieldMetrics(self):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_CollectQualityYieldMetrics''')
            cmd=f'''{self.gatk} CollectQualityYieldMetrics -I {self.bam} -O {output}.txt'''
            with open(f'{self.output_path}/gatk_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)


    def MeanQualityByCycle(self):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_MeanQualityByCycle''')
            cmd=f'''{self.gatk} MeanQualityByCycle -I {self.bam} -O {output}.txt -CHART {output}.pdf'''
            with open(f'{self.output_path}/gatk_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)


    def QualityScoreDistribution(self):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_QualityScoreDistribution''')
            cmd=f'''{self.gatk} QualityScoreDistribution -I {self.bam} -O {output}.txt -CHART {output}.pdf'''
            with open(f'{self.output_path}/gatk_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)

    def CollectHsMetrics(self,bait,call_bed):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_CollectHsMetrics''')
            cmd=f'''{self.gatk} CollectHsMetrics -I {self.bam} -O {output}.txt --BAIT_INTERVALS {bait} --TARGET_INTERVALS {call_bed}'''
            with open(f'{self.output_path}/gatk_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)

    def CollectSequencingArtifactMetrics(self):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_CollectSequencingArtifactMetrics''')
            cmd = f'''{self.gatk} CollectSequencingArtifactMetrics -I {self.bam} -R {ref} -O {output}.txt'''
            with open(f'{self.output_path}/gatk_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)
    def CollectTargetedPcrMetrics(self,bait,call_bed):
        if check_file(self.bam):
            output = os.path.join(self.output_path, f'''{self.sample}_CollectTargetedPcrMetrics''')
            cmd=f'''{self.gatk} CollectTargetedPcrMetrics -I {self.bam} -O {output}.txt --AMPLICON_INTERVALS {bait} --TARGET_INTERVALS {call_bed}'''
            with open(f'{self.output_path}/gatk_run.sh','a') as fp:
                fp.writelines(cmd+'\n\n')
            return cmd_run(cmd,f'{output}.log')
        else:
            print('the file no exist:', self.bam)








if __name__ == '__main__':
    pass
