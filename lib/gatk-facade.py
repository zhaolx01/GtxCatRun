#!/usr/bin/env python
#
# Launcher script for GATK tools. Delegates to java -jar, spark-submit, or gcloud as appropriate,
# and sets many important Spark and htsjdk properties before launch.
#
# If running a non-Spark tool, or a Spark tool in local mode, will search for GATK executables
# as follows:
#     -If the GATK_LOCAL_JAR environment variable is set, uses that jar
#     -Otherwise if the GATK_RUN_SCRIPT created by "gradle installDist" exists, uses that
#     -Otherwise uses the newest local jar in the same directory as the script or the BIN_PATH
#      (in that order of precedence)
#
# If running a Spark tool, searches for GATK executables as follows:
#     -If the GATK_SPARK_JAR environment variable is set, uses that jar
#     -Otherwise uses the newest Spark jar in the same directory as the script or the BIN_PATH
#      (in that order of precedence)
#

from queue import Empty
import sys
from subprocess import check_call, CalledProcessError, call
import os
import signal
import re
import tempfile
import multiprocessing
import shutil

script = os.path.dirname(os.path.realpath(__file__))

projectName = "gatk"

BUILD_LOCATION = script +"/build/install/" + projectName + "/bin/"
GATK_RUN_SCRIPT = BUILD_LOCATION + projectName
GATK_LOCAL_JAR_ENV_VARIABLE = "GATK_LOCAL_JAR"

BIN_PATH = script + "/build/libs"

PACKAGED_LOCAL_JAR_OPTIONS= ["-Dsamjdk.use_async_io_read_samtools=false",
                  "-Dsamjdk.use_async_io_write_samtools=true",
                  "-Dsamjdk.use_async_io_write_tribble=false",
                  "-Dsamjdk.compression_level=6"]


class GATKLaunchException(Exception):
    pass


def signal_handler(signal, frame):
    sys.exit(1)

def main(args):
    #suppress stack trace when killed by keyboard interrupt
    signal.signal(signal.SIGINT, signal_handler)

    try:
        if len(args) == 0 or (len(args) == 1 and (args[0] == "--help" or args[0] == "-h")):
            print("")
            print(" Usage template for all tools")
            print("    gatk AnyTool toolArgs")
            print("")
            print(" Getting help")
            print("    gatk --list       Print the list of available tools" )
            print("")
            print("    gatk Tool --help  Print help on a particular tool" )
            print("")
            print(" Configuration File Specification")
            print("     --gatk-config-file                PATH/TO/GATK/PROPERTIES/FILE")
            print("")
            print(" gatk forwards commands to GATK and adds some sugar for submitting spark jobs")
            print("")
            print("   --java-options 'OPTION1[ OPTION2=Y ... ]'   optional - pass the given string of options to the ")
            print("                 java JVM at runtime.  ")
            print("                 Java options MUST be passed inside a single string with space-separated values.")
            sys.exit(0)

        if len(args) == 1 and args[0] == "--list":
            args[0] = "--help"  # if we're invoked with --list, invoke the GATK with --help

        javaOptions = getValueForArgument(args, "--java-options")
        if javaOptions is not None:
            i = args.index("--java-options")
            del args[i] #remove javaOptions
            del args[i] #and its parameter

        runGATK(args, javaOptions)

    except GATKLaunchException as e:
        sys.stderr.write(str(e)+"\n")
        sys.exit(3)
    except CalledProcessError as e:
        sys.exit(e.returncode)

def getLocalGatkRunCommand(javaOptions):
    localJarFromEnv = getJarFromEnv(GATK_LOCAL_JAR_ENV_VARIABLE)

    # Add java options to our packaged local jar options
    if javaOptions is not None:
        PACKAGED_LOCAL_JAR_OPTIONS.extend(javaOptions.split())

    if localJarFromEnv is not None:
        return formatLocalJarCommand(localJarFromEnv)

    return formatLocalJarCommand(getLocalJar())  # will throw if local jar not found


def formatLocalJarCommand(localJar):
    return ["java"] + PACKAGED_LOCAL_JAR_OPTIONS + [ "-jar", localJar]

def getLocalJar(throwIfNotFound=True):
    localJar = findJar("local.jar", envVariableOverride=GATK_LOCAL_JAR_ENV_VARIABLE)
    if localJar is None and throwIfNotFound:
        raise GATKLaunchException("No local jar was found, please export " + GATK_LOCAL_JAR_ENV_VARIABLE + "=<path_to_local_jar>")
    return localJar


def findJar(jarSuffix, jarPrefix=projectName, envVariableOverride=None, jarSearchDirs=(script, BIN_PATH)):
    if envVariableOverride is not None:
        jarPathFromEnv = getJarFromEnv(envVariableOverride)
        if jarPathFromEnv is not None:
            return jarPathFromEnv

    for jarDir in jarSearchDirs:
        jar = getNewestJarInDir(jarDir, jarSuffix, jarPrefix)
        if jar is not None:
            sys.stderr.write("Using GATK jar " + jar)
            return jar

    return None

def getJarFromEnv(envVariableName):
    jarPathFromEnv = os.environ.get(envVariableName)
    if jarPathFromEnv is not None:
        if not os.path.exists(jarPathFromEnv):
            raise GATKLaunchException(envVariableName + " was set to: " + jarPathFromEnv + " but this file doesn't exist. Please fix your environment")
        else:
            sys.stderr.write("Using GATK jar " + jarPathFromEnv + " defined in environment variable " + envVariableName)
            return jarPathFromEnv

    return None

def getNewestJarInDir(dir, jarSuffix, jarPrefix):
    if not os.path.exists(dir):
        return None

    dirContents = os.listdir(dir)
    jarPattern = re.compile("^" + jarPrefix + ".*" + jarSuffix + "$")
    jars = [f for f in dirContents if jarPattern.match(f)]
    if len(jars) != 0:
        newestJar = max(jars, key=lambda x: os.stat(dir + "/" + x).st_mtime)
        return dir + "/" + newestJar

    return None

def runGATK(gatkArgs, javaOptions):
    program = getLocalGatkRunCommand(javaOptions)
    splitCommand = {"HaplotypeCaller", "Mutect2"}
    if gatkArgs[0] in splitCommand:
        intervals = getValueForArgument(gatkArgs, "--intervals,-L")
        needRemove = False
        if intervals is not None:
            if not os.path.isfile(intervals):
                intervals = None
        else:
            intervals = makeIntervals(gatkArgs)
            needRemove = True

        if intervals is not None:
            intervalsOutDir=tempfile.NamedTemporaryFile(delete=True).name
            os.mkdir(intervalsOutDir)
            args = "IntervalListTools \
                    --SCATTER_COUNT 512 \
                    --SUBDIVISION_MODE BALANCING_WITHOUT_INTERVAL_SUBDIVISION_WITH_OVERFLOW \
                    --UNIQUE true --SORT true \
                    --INPUT {} --OUTPUT {}".format(intervals, intervalsOutDir)
            check_call(program + args.split())
            if needRemove:
                os.remove(intervals)

            files = os.listdir(intervalsOutDir)
            if files is not Empty:
                files.sort()
                vcf = getValueForArgument(gatkArgs, "--OUTPUT,-O")
                removeValueForArgument(gatkArgs, "--intervals,-L")
                removeValueForArgument(gatkArgs, "--OUTPUT,-O")
                poSize = min(multiprocessing.cpu_count(), len(files))
                po = multiprocessing.Pool(poSize)
                inputs = []
                for dir in files:
                    dir = os.path.join(intervalsOutDir, dir)
                    cmd = program + gatkArgs + ["-L", os.path.join(dir, "scattered.interval_list")]
                    cmd += ["-O", os.path.join(dir, "scattered.vcf.gz")]
                    inputs += ["-I", os.path.join(dir, "scattered.vcf.gz")]
                    po.apply_async(runCommand, (cmd,))
                po.close()
                po.join()

                check_call(program + ["MergeVcfs"] + inputs + ["-O", vcf])
                shutil.rmtree(intervalsOutDir)
                return
            shutil.rmtree(intervalsOutDir)

    runCommand(program + gatkArgs)


def makeIntervals(gatkArgs):
    refPath = getValueForArgument(gatkArgs, "--reference,-R")
    if refPath is not None:
        refIdx = refPath + ".fai"
        refDict = refPath + ".dict"
        if not os.path.isfile(refDict):
            refDict = os.path.splitext(refPath)[0] + ".dict"
        if os.path.isfile(refIdx) and os.path.isfile(refDict):
            cmd = 'awk -v FS="\t" -v OFS="\t" \'{print $1 FS "0" FS ($2-1)}\' ' + refIdx
            bed = tempfile.NamedTemporaryFile(delete=True)
            call(cmd, stdout=bed, shell=True)
            program = getLocalGatkRunCommand(None)
            intervals = tempfile.NamedTemporaryFile(delete=True).name + ".interval_list"
            args = "BedToIntervalList -I {} -SD {} -O {}".format(bed.name, refDict, intervals)
            check_call(program + args.split())
            return intervals

    return None

def runCommand(cmd):
    sys.stderr.write( "\nRunning:\n")
    sys.stderr.write("    " + " ".join(cmd)+"\n")
    gatk_env = os.environ.copy()
    gatk_env["SUPPRESS_GCLOUD_CREDS_WARNING"] = "true"
    check_call(cmd, env=gatk_env)

def getValueForArgument(args, argument):
    for argu in argument.split(","):
        if argu in args:
            i = args.index(argu)
            if len(args) <= i+1:
                raise GATKLaunchException("Argument: " + argu + " requires a parameter")
            return args[i+1]
    return None

def removeValueForArgument(args, argument):
    for argu in argument.split(","):
        if argu in args:
            i = args.index(argu)
            if len(args) <= i+1:
                raise GATKLaunchException("Argument: " + argu + " requires a parameter")
            del args[i : i+2]

if __name__ == "__main__":
    main(sys.argv[1:])
