#!/bin/bash
#SBATCH -N 100 
#SBATCH -p compute2 
#SBATCH -t 04:00:00 
#SBATCH -A bk1040

source ../source.sh

mkdir results

for REP in 1 2 ; do  # 3
for PPN in 1 2 4 6 8 12 ; do  # y must be a multiple of ppn

D=10:12000:12000:200
PC=$(($SLURM_JOB_NUM_NODES*$PPN))
echo "Running $PC with $PPN and $SLURM_JOB_NUM_NODES"
export MPI="srun -n $PC --distribution=cyclic:cyclic"

$MPI hostname

for TEST in lustre01.conf lustre-both.conf ; do
ln -sf /home/dkrz/k202079/work/esdm/esdm-test-apps/mistral-conf/$TEST esdm.conf
(
echo 
mkfs.esdm -g -l --create --remove --ignore-errors 1>/dev/null 2>&1
$MPI ./benchtool -d=$D -f="esdm://test.esdm" -n=$SLURM_JOB_NUM_NODES -p=$PPN -w -r
#srun -n $PC ./benchtool -r -d=$D -f="esdm://test.esdm" -n=$SLURM_JOB_NUM_NODES -p=$PPN # performance was the same
#srun -n $PC ./benchtool -r --verify -d=$D -f="esdm://test.esdm" -n=$SLURM_JOB_NUM_NODES -p=$PPN # verification was OK
find _metadummy/
find /mnt/lustre01/work/bk1040/k202079/_esdm -type f -exec ls -l \{\} \;
find /mnt/lustre02/work/bk1040/k202079/_esdm -type f -exec ls -l \{\} \;
mkfs.esdm -g -l --create --remove --ignore-errors 1>/dev/null 2>&1
) >> results/esdm-$TEST-$SLURM_JOB_NUM_NODES-$PPN.txt 2<&1
done

(
rm -rf /mnt/lustre01/work/ku0598/k202079/test
mkdir /mnt/lustre01/work/ku0598/k202079/test
lfs setstripe -c $(($SLURM_JOB_NUM_NODES*2)) /mnt/lustre01/work/ku0598/k202079/test

echo 
$MPI ./benchtool -d=$D -f="/mnt/lustre01/work/ku0598/k202079/test/file.nc" -n=$SLURM_JOB_NUM_NODES -p=$PPN -w -r
ls -lah /mnt/lustre01/work/ku0598/k202079/test/*
lfs getstripe /mnt/lustre01/work/ku0598/k202079/test/*
rm -rf /mnt/lustre01/work/ku0598/k202079/test/*
) >> results/nc-$SLURM_JOB_NUM_NODES-$PPN.txt 2>&1

(
echo 
rm -rf /mnt/lustre01/work/ku0598/k202079/test
mkdir /mnt/lustre01/work/ku0598/k202079/test
lfs setstripe -c 1 /mnt/lustre01/work/ku0598/k202079/test

$MPI ./benchtool -d=$D -f="/mnt/lustre01/work/ku0598/k202079/test/test" -n=$SLURM_JOB_NUM_NODES -p=$PPN -w -r -t=file-per-process
lfs getstripe /mnt/lustre01/work/ku0598/k202079/test/*
ls -lah /mnt/lustre01/work/ku0598/k202079/test/*
rm /mnt/lustre01/work/ku0598/k202079/test/*
) >> results/nc-fpp-$SLURM_JOB_NUM_NODES-$PPN.txt 2>&1

#fi

done
done

echo "[OK]"
