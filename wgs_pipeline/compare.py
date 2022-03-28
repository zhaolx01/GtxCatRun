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
from lib.tools import check_file

con=TestConfig()
happy=con.get_docker("happy")
benchmark_versions=con.get_project_info("benchmark_versions")


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("sample",type=str,help="sample name ",default='HG001')
    parser.add_argument("-vs_sites",type=str,choices=["gatk_vs_gtx","benchmark_vs_gtx","benchmark_vs_gatk"])
    parser.add_argument("--gatk_version",type=str,choices=['4.1.7.0','4.1.8.1','4.1.9.0','4.2.3.0','4.2.4.1','4.2.5.0'],default='4.1.8.1')
    parser.add_argument("--gtx_version",type=str,choices=['2.1.0-pre1','2.0.1-pre2'],default='2.1.0-pre1')
    parser.add_argument("--call_bed",type=str)
    parser.add_argument("--CPU", type=int, default=60)
    args = parser.parse_args()
    return args


class Happy_vs:
    def __init__(self,sample,CPU=60):
        self.sample=sample
        #ref转相对路径
        self.ref=con.get_ref("bwa_index").replace(BASE_DIR+'/','')
        self.CPU=CPU
        #检测镜像或者准备镜像

    def gatk_vs_gtx(self,gatk_version,gtx_version,call_bed=''):
        if call_bed:
            gatk_vcf=os.path.join(con.get_analysis("wes_output_path"),f'{self.sample}/gatk_{gatk_version}/{self.sample}.vcf.gz')
            gtx_vcf=os.path.join(con.get_analysis("wes_output_path"),f'{self.sample}/gtx_{gtx_version}/{self.sample}.vcf.gz')
            output=os.path.join(con.get_analysis("wes_benchmark_result_path"),f'gatk-{gatk_version}_vs_gtx-{gtx_version}')
            #gtx-v2.1_vs_gatk-4.1.x
        else:
            gatk_vcf = os.path.join(con.get_analysis("wgs_output_path"),
                                    f'{self.sample}/gatk_{gatk_version}/{self.sample}.vcf.gz')
            gtx_vcf = os.path.join(con.get_analysis("wgs_output_path"),
                                   f'{self.sample}/gtx_{gtx_version}/{self.sample}.vcf.gz')
            output= os.path.join(con.get_analysis("wgs_benchmark_result_path"),f'gatk-{gatk_version}_vs_gtx-{gtx_version}')
        print('----output dir:',output)
        os.makedirs(output,exist_ok=True)
        log_path=output
        if check_file(gtx_vcf) and check_file(gatk_vcf):
            # 将绝对路径转相对路径，方便docker使用
            gatk_vcf = gatk_vcf.replace(BASE_DIR + '/', '')
            gtx_vcf = gtx_vcf.replace(BASE_DIR + '/', '')
            output = output.replace(BASE_DIR + '/', '')
            print('-----',output)

            cmd=f'''docker run -v {BASE_DIR}:/data -w /data {happy} /opt/hap.py/bin/hap.py {gatk_vcf} {gtx_vcf} -r {self.ref} -o {output}/{self.sample}_gatk-{gatk_version}_vs_gtx-{gtx_version} --threads {self.CPU} --engine vcfeval'''
            #保存比较命令：
            with open(f'{log_path}/vs.sh','a') as f:
                f.writelines(cmd+'\n\n')
            if cmd_run(cmd,f'{log_path}/{self.sample}vs.log'):
                print(self.sample,'vs over')
            else:
                print(self.sample, 'vs Error!')
        else:
            print('vcf no exist!!')


    def benchmark_vs_gtx(self,gtx_version,call_bed=''):
        benchmark_vcf=os.path.join(con.get_data("benchmark_vcf_path"),f'{benchmark_versions}/{self.sample}_GRCh38_1_22_v4.2.1_benchmark.vcf.gz')
        confident_bed=os.path.join(con.get_data("benchmark_vcf_path"),f'{benchmark_versions}/{self.sample}_GRCh38_1_22_v4.2.1_benchmark.bed')
        print(con.get_data("benchmark_vcf_path"))
        print(benchmark_vcf)
        if call_bed:
            gtx_vcf=os.path.join(con.get_analysis("wes_output_path"),f'{self.sample}/gtx_{gtx_version}/{self.sample}.vcf.gz')
            output=os.path.join(con.get_analysis("wes_benchmark_result_path"),f'{benchmark_versions}_vs_gtx-{gtx_version}')
            call_bed=os.path.join(con.get_data("wes_data"), call_bed).replace(BASE_DIR + '/', '')
            #benchmark_vs_gtx-v2.1
        else:
            gtx_vcf = os.path.join(con.get_analysis("wgs_output_path"),
                                   f'{self.sample}/gtx_{gtx_version}/{self.sample}.vcf.gz')
            output= os.path.join(con.get_analysis("wgs_benchmark_result_path"),
                                       f'{benchmark_versions}_vs_gtx-{gtx_version}')


        os.makedirs(f'{output}',exist_ok=True)
        log_path=output
        if check_file(gtx_vcf) and check_file(benchmark_vcf):
            # 将绝对路径转相对路径，方便docker使用
            benchmark_vcf = benchmark_vcf.replace(BASE_DIR + '/', '')
            gtx_vcf = gtx_vcf.replace(BASE_DIR + '/', '')
            output = output.replace(BASE_DIR + '/', '')
            confident_bed=confident_bed.replace(BASE_DIR + '/', '')


            cmd=f'''docker run -v {BASE_DIR}:/data -w /data {happy} /opt/hap.py/bin/hap.py {benchmark_vcf} {gtx_vcf} -r {self.ref} -o {output}/{self.sample}_{benchmark_versions}_vs_gtx-{gtx_version} --threads {self.CPU} --engine vcfeval -f {confident_bed}'''

            if call_bed:
                cmd=cmd+f' -R {call_bed}'
            #保存比较命令：
            with open(f'{log_path}/vs.sh','a') as f:
                f.writelines(cmd+'\n\n')
            if cmd_run(cmd,f'{log_path}/{self.sample}vs.log'):
                print(self.sample,'vs over')
            else:
                print(self.sample, 'vs Error!')
        else:
            print('vcf no exist!!')

    def benchmark_vs_gatk(self,gatk_version,call_bed=''):
        benchmark_vcf = os.path.join(con.get_data("benchmark_vcf_path"),
                                     f'{benchmark_versions}/{self.sample}_GRCh38_1_22_v4.2.1_benchmark.vcf.gz')
        confident_bed = os.path.join(con.get_data("benchmark_vcf_path"),
                                     f'{benchmark_versions}/{self.sample}_GRCh38_1_22_v4.2.1_benchmark.bed')
        if call_bed:
            gatk_vcf=os.path.join(con.get_analysis("wes_output_path"),f'{self.sample}/gatk_{gatk_version}/{self.sample}.vcf.gz')
            output = os.path.join(con.get_analysis("wes_benchmark_result_path"), f'{benchmark_versions}_vs_gatk-{gatk_version}')
            call_bed=os.path.join(con.get_data("wes_data"), call_bed).replace(BASE_DIR + '/', '')
            # benchmark_vs_gtx-v2.1
        else:
            gatk_vcf=os.path.join(con.get_analysis("wgs_output_path"),f'{self.sample}/gatk_{gatk_version}/{self.sample}.vcf.gz')
            output = os.path.join(con.get_analysis("wgs_benchmark_result_path"),
                                  f'{benchmark_versions}_vs_gatk-{gatk_version}')

        os.makedirs(f'{output}', exist_ok=True)
        log_path = output
        if check_file(gatk_vcf) and check_file(benchmark_vcf):
            # 将绝对路径转相对路径，方便docker使用
            benchmark_vcf = benchmark_vcf.replace(BASE_DIR + '/', '')
            gatk_vcf = gatk_vcf.replace(BASE_DIR + '/', '')
            output = output.replace(BASE_DIR + '/', '')
            confident_bed = confident_bed.replace(BASE_DIR + '/', '')

            cmd = f'''docker run -v {BASE_DIR}:/data -w /data {happy} /opt/hap.py/bin/hap.py {benchmark_vcf} {gatk_vcf} -r {self.ref} -o {output}/{self.sample}_{benchmark_versions}_vs_gatk-{gatk_version} --threads {self.CPU} --engine vcfeval -f {confident_bed}'''

            if call_bed:
                cmd = cmd + f' -R {call_bed}'
            # 保存比较命令：
            with open(f'{log_path}/vs.sh', 'a') as f:
                f.writelines(cmd + '\n\n')
            if cmd_run(cmd, f'{log_path}/{self.sample}vs.log'):
                print(self.sample, 'vs over')
            else:
                print(self.sample, 'vs Error!')

        else:
            print('vcf no exist!!')

    def gatk_vs_gtx_mutect2(self,gatk_version,gtx_version,normal_sample,tumor_sample,call_bed=''):

        if call_bed:
            gatk_vcf=os.path.join(con.get_analysis("wes_mutect2_output_path"),f'{normal_sample}-{tumor_sample}/gatk_{gatk_version}/{normal_sample}_{tumor_sample}.FilterMutectCalls.tar.gz')
            gtx_vcf=os.path.join(con.get_analysis("wes_mutect2_output_path"),f'{normal_sample}-{tumor_sample}/gtx_{gtx_version}/{normal_sample}_{tumor_sample}.FilterMutectCalls.vcf.gz')
            output=os.path.join(con.get_analysis("wes_mutect2_benchmark_result_path"),f'gatk-{gatk_version}_vs_gtx-{gtx_version}')
            #gtx-v2.1_vs_gatk-4.1.x
        else:
            gatk_vcf = os.path.join(con.get_analysis("wgs_mutect2_output_path"),
                                    f'{normal_sample}-{tumor_sample}/gatk_{gatk_version}/{normal_sample}_{tumor_sample}.FilterMutectCalls.tar.gz')
            gtx_vcf = os.path.join(con.get_analysis("wgs_mutect2_output_path"),
                                   f'{normal_sample}-{tumor_sample}/gtx_{gtx_version}/{normal_sample}_{tumor_sample}.FilterMutectCalls.vcf.gz')
            output = os.path.join(con.get_analysis("wgs_mutect2_benchmark_result_path"),
                                  f'gatk-{gatk_version}_vs_gtx-{gtx_version}')
        print('----output dir:',output)
        os.makedirs(output,exist_ok=True)
        log_path=output
        if check_file(gtx_vcf) and check_file(gatk_vcf):
            # 将绝对路径转相对路径，方便docker使用
            gatk_vcf = gatk_vcf.replace(BASE_DIR + '/', '')
            gtx_vcf = gtx_vcf.replace(BASE_DIR + '/', '')
            output = output.replace(BASE_DIR + '/', '')
            print('-----',output)
           #-o output/eval -r $fasta -N $truth_vcf $calls_vcf --no-fixchr-truth --no-fixchr-query
            cmd=f'''docker run -v {BASE_DIR}:/data -w /data {happy} /opt/hap.py/bin/som.py {gatk_vcf} {gtx_vcf} -r {self.ref} \
                     -o {output}/{normal_sample}_{tumor_sample}_gatk-{gatk_version}_vs_gtx-{gtx_version} --no-fixchr-truth --no-fixchr-query'''
            #保存比较命令：
            with open(f'{log_path}/vs.sh','a') as f:
                f.writelines(cmd+'\n\n')
            if cmd_run(cmd,f'{log_path}/{normal_sample}_{tumor_sample}vs.log'):
                print(f'{normal_sample} {tumor_sample}','vs over')
            else:
                print(f'{normal_sample} {tumor_sample}', 'vs Error!')
        else:
            print('vcf no exist!!')


def run():
    arg=arguments()
    sample=arg.sample
    vs_sites=arg.vs_sites
    gatk_version=arg.gatk_version
    gtx_version=arg.gtx_version
    CPU=arg.CPU
    call_bed=arg.call_bed
    happy_vs = Happy_vs(sample,CPU)

    if vs_sites=='gatk_vs_gtx':
        happy_vs.gatk_vs_gtx(gatk_version,gtx_version,call_bed=call_bed)
    elif vs_sites=='benchmark_vs_gtx':
        happy_vs.benchmark_vs_gtx(gtx_version,call_bed=call_bed)
    elif vs_sites=='benchmark_vs_gatk':
        happy_vs.benchmark_vs_gatk(gatk_version,call_bed=call_bed)
    else:
        print('vs sites error!!')


if __name__=="__main__":
    sample='HG001'
    gatk_version='4.1.8.1'
    gtx_version='2.1.0-pre1'
    call_bed='S31285117_Regions_hg38.bed'
    happy_vs=Happy_vs(sample)
    #happy_vs.gatk_vs_gtx(gatk_version, gtx_version, call_bed=call_bed)
    happy_vs.benchmark_vs_gtx(gtx_version,call_bed=call_bed)




