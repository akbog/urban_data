#!/bin/sh

#SBATCH --nodes=1
#SBATCH --output="slurm-%j.out"

#SBATCH --time=01:30:00

#SBATCH --job-name=sparktest

#SBATCH --partition=aquila

#SBATCH --ntasks-per-node=2
#SBATCH --exclusive
#SBATCH --no-kill


module load anaconda3/5.2.0 java/1.8.0_131 spark/2.4.6-hd2.7
export MAGPIE_SUBMISSION_TYPE="sbatchsrun"


export MAGPIE_SCRIPTS_HOME="${HOME}/bin/magpie"
mkdir -p /tmp/${USER}/magpie
export MAGPIE_LOCAL_DIR="/tmp/${USER}/magpie"

export MAGPIE_JOB_TYPE="spark"

# export MAGPIE_STARTUP_TIME=30
# export MAGPIE_SHUTDOWN_TIME=30

# export MAGPIE_ENVIRONMENT_VARIABLE_SCRIPT="${HOME}/my-job-env"

#
# export MAGPIE_ENVIRONMENT_VARIABLE_SCRIPT_SHELL="/bin/bash"

#
# export MAGPIE_REMOTE_CMD="ssh"
# export MAGPIE_REMOTE_CMD_OPTS=""

export JAVA_HOME="/gpfsnyu/packages/java/jdk1.8.0_131"

# MAGPIE_PYTHON path used for:
# - Spark PySpark path
# - Launching tensorflow tasks
export MAGPIE_PYTHON="/gpfsnyu/packages/anaconda3/5.2.0/bin/python"

#
export SPARK_SETUP=yes

# Set Spark Setup Type
#
export SPARK_SETUP_TYPE="STANDALONE"

# Version
#
export SPARK_VERSION="2.4.6-hd2.7"

#
export SPARK_HOME="/gpfsnyu/packages/spark/${SPARK_VERSION}" #  "${HOME}/spark-${SPARK_VERSION}"

#
mkdir -p /tmp/${USER}/spark
export SPARK_LOCAL_DIR="/tmp/${USER}/spark"

#
# export SPARK_WORKER_MEMORY_PER_NODE=16000

#
# export SPARK_WORKER_DIRECTORY=/tmp/${USER}/spark/work

#
# export SPARK_JOB_MEMORY="2048"

#
# export SPARK_DRIVER_MEMORY="2048"

#
# export SPARK_DAEMON_HEAP_MAX=2000

#
# export SPARK_ENVIRONMENT_EXTRA_PATH="${HOME}/spark-my-environment"


# Set spark job for MAGPIE_JOB_TYPE = spark
#
export SPARK_JOB="sparkpi"

#

#
# export SPARK_MEMORY_STORAGE_FRACTION=0.5

# SPARK_STORAGE_MEMORY_FRACTION
#
#
# export SPARK_STORAGE_MEMORY_FRACTION=0.6

#
# export SPARK_SHUFFLE_MEMORY_FRACTION=0.2

# SPARK_RDD_COMPRESS
#
# Should RDD's be compressed by default?  Defaults to true.  In HPC
# environments with parallel file systems or local storage, the cost
# of compressing / decompressing RDDs is likely a be a net win over
# writing data to a parallel file system or using up the limited
# amount of local storage space available.  However, for some users
# this cost may not be worthwhile and should be disabled.
#
# Note that only serialized RDDs are compressed, such as with storage
# level MEMORY_ONLY_SER or MEMORY_AND_DISK_SER.  All python RDDs are
# serialized by default.
#
# Defaults to true.
#
# export SPARK_RDD_COMPRESS=true

# SPARK_IO_COMPRESSION_CODEC
#
# Defaults to lz4, can specify snappy, lz4, lzf, snappy, or zstd
#
# export SPARK_IO_COMPRESSION_CODEC=lz4

# SPARK_DEPLOY_SPREADOUT
#
# Per Spark documentation, "Whether the standalone cluster manager
# should spread applications out across nodes or try to consolidate
# them onto as few nodes as possible. Spreading out is usually better
# for data locality in HDFS, but consolidating is more efficient for
# compute-intensive workloads."
#
# If you are hard coding parallelism in certain parts of your
# application because those individual actions do not scale well, it
# may be beneficial to disable this.
#
# Defaults to true
#
# export SPARK_DEPLOY_SPREADOUT=true

# SPARK_JOB_CLASSPATH
#
# May be necessary to set to get certain code/scripts to work.
#
# e.g. to run a Spark example, you may need to set
#
# export SPARK_JOB_CLASSPATH="examples/target/spark-examples-assembly-0.9.1.jar"
#
# Note that this is primarily for Spark 0.9.1 and earlier versions.
# You likely want to use the --driver-class-path option in
# spark-submit now.
#
# export SPARK_JOB_CLASSPATH=""

# SPARK_JOB_LIBRARY_PATH
#
# May be necessary to set to get certain code/scripts to work.
#
# Note that this is primarily for Spark 0.9.1 and earlier versions.
# You likely want to use the --driver-library-path option in
# spark-submit now.
#
# export SPARK_JOB_LIBRARY_PATH=""

# SPARK_JOB_JAVA_OPTS
#
# May be necessary to set options to set Spark options
#
# e.g. -Dspark.default.parallelism=16
#
# Magpie will set several options on its own, however, these options
# will be appended last, ensuring they override anything that Magpie
# will set by default.
#
# Note that many of the options that were set in SPARK_JAVA_OPTS in
# Spark 0.9.1 and earlier have been deprecated.  You likely want to
# use the --driver-java-options option in spark-submit now.
#
# export SPARK_JOB_JAVA_OPTS=""

# SPARK_LOCAL_SCRATCH_DIR
#
# By default, if Hadoop is setup with a file system, the Spark local
# scratch directory, where scratch data is placed, will automatically
# be calculated and configured.  If Hadoop is not setup, the following
# must be specified.
#
# If you have local SSDs or NVRAM stored on the nodes of your system,
# it may be in your interest to set this to a local drive.  It can
# improve performance of both shuffling and disk based RDD
# persistence.  If you want to specify multiple paths (such as
# multiple drives), make them comma separated
# (e.g. /dir1,/dir2,/dir3).
#
# Note that this field will not work if SPARK_SETUP_TYPE="YARN".
# Please set HADOOP_LOCALSTORE to inform Yarn to set a local SSD for
# Yarn to use for local scratch.
#
export SPARK_LOCAL_SCRATCH_DIR="/scratch/${USER}/sparkscratch/"

# SPARK_LOCAL_SCRATCH_DIR_CLEAR
#
# After your job has completed, if SPARK_LOCAL_SCRATCH_DIR_CLEAR is
# set to yes, Magpie will do a rm -rf on all directories in
# SPARK_LOCAL_SCRATCH_DIR.  This is particularly useful if the local
# scratch directory is on local storage and you want to clean up your
# work before the next user uses the node.
#
# export SPARK_LOCAL_SCRATCH_DIR_CLEAR="yes"

# SPARK_NETWORK_TIMEOUT
#
# This will configure many network timeout configurations within
# Spark.  If you see that your jobs are regularly failing with timeout
# issues, try increasing this value.  On large HPC systems, timeouts
# may occur more often, such as on loaded parallel file systems or
# busy networks.
#
# As of this version, this will configure:
#
# spark.network.timeout
# spark.files.fetchTimeout
# spark.rpc.askTimeout
# spark.rpc.lookupTimeout
# spark.core.connection.ack.wait.timeout
# spark.shuffle.registration.timeout
# spark.network.auth.rpcTimeout
# spark.shuffle.sasl.timeout
#
# Note that some of this fields will only effect newer spark versions.
#
# Specified in seconds, by default 120.
#
# export SPARK_NETWORK_TIMEOUT=120

# SPARK_YARN_STAGING_DIR
#
# By default, Spark w/ Yarn will use your home directory for staging
# files for a job.  This home directory must be accessible by all
# nodes.
#
# This may pose a problem if you are not using HDFS and your home
# directory is not NFS or network mounted.  Set this value to a
# network location as your staging directory.  Be sure to prefix this
# path the appropriate scheme, such as file://.
#
# This option is only available beginning in Spark 2.0.
#
# export SPARK_YARN_STAGING_DIR="file:///lustre/${USER}/sparkStaging/"

############################################################################
# Spark SparkPi Configuration
############################################################################

# SparkPi Slices
#
# Number of "slices" to parallelize in Pi estimation.  Generally
# speaking, more should lead to more accurate estimates.
#
# If not specified, equals number of nodes.
#
# export SPARK_SPARKPI_SLICES=4

############################################################################
# Spark SparkWordCount Configuration
############################################################################

# SparkWordCount File
#
# Specify the file to do the word count on.  Specify the scheme, such
# as hdfs:// or file://, appropriately.
#
# export SPARK_SPARKWORDCOUNT_FILE="/mywordcountfile"

# SparkWordCount Copy In File
#
# In some cases, a file must be copied in before it can be used.  Most
# notably, this can be the case if the file is not yet in HDFS.
#
# If specified below, the file will be copied to the location
# specified by SPARK_SPARKWORDCOUNT_FILE before the word count is
# executed.
#
# Specify the scheme appropriately.  At this moment, the schemes of
# file:// and hdfs:// are recognized for this option.
#
# Note that this is not required.  The file could be copied in any
# number of other ways, such as through a previous job or through a
# script specified via MAGPIE_PRE_JOB_RUN.
#
# export SPARK_SPARKWORDCOUNT_COPY_IN_FILE="/mywordcountfile"

############################################################################
# Run Job
############################################################################

srun --no-kill -W 0 $MAGPIE_SCRIPTS_HOME/magpie-check-inputs
if [ $? -ne 0 ]
then
    exit 1
fi
srun --no-kill -W 0 $MAGPIE_SCRIPTS_HOME/magpie-setup-core
if [ $? -ne 0 ]
then
    exit 1
fi
srun --no-kill -W 0 $MAGPIE_SCRIPTS_HOME/magpie-setup-projects
if [ $? -ne 0 ]
then
    exit 1
fi
srun --no-kill -W 0 $MAGPIE_SCRIPTS_HOME/magpie-setup-post
if [ $? -ne 0 ]
then
    exit 1
fi
srun --no-kill -W 0 $MAGPIE_SCRIPTS_HOME/magpie-pre-run
if [ $? -ne 0 ]
then
    exit 1
fi
srun --no-kill -W 0 $MAGPIE_SCRIPTS_HOME/magpie-run
srun --no-kill -W 0 $MAGPIE_SCRIPTS_HOME/magpie-cleanup
srun --no-kill -W 0 $MAGPIE_SCRIPTS_HOME/magpie-post-run

rm -rf /tmp/${USER}/magpie
rm -rf /tmp/${USER}/spark
