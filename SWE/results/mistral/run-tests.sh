#!/bin/bash
#SBATCH -N 10 
#SBATCH -p compute2 
#SBATCH -t 04:00:00 
#SBATCH -A bk1040

source ../source.sh

mkdir results
C=10
X=23040
Y=$X
OUT=/mnt/lustre01/work/ku0598/k202079/test

rm -rf $OUT || exit 1
mkdir $OUT || exit 1
lfs setstripe -c 128 $OUT

for REP in 1 2 3 ; do 
for PPN in 1 2 4 6 8 12 ; do 

PC=$(($SLURM_JOB_NUM_NODES*$PPN))

for TEST in lustre01.conf lustre-both.conf ; do

ln -sf /home/dkrz/k202079/work/esdm/esdm-test-apps/mistral-conf/$TEST esdm.conf
(
echo 

mkfs.esdm -g -l --create --remove --ignore-errors 1>/dev/null 2>&1
date
/usr/bin/time srun -n $PC ./build/SWE_gnu_release_mpi_fwave.esdm -x $X -y $Y -o "out" -c $C
date
find _metadummy/
find /mnt/lustre02/work/bk1040/k202079/_esdm -type f -exec ls -l \{\} \;
find /mnt/lustre01/work/ku0598/k202079/_esdm -type f -exec ls -l \{\} \;
mkfs.esdm -g -l --create --remove --ignore-errors 1>/dev/null 2>&1
) >> results/esdm-$TEST-$SLURM_JOB_NUM_NODES-$PPN.txt 2>&1
done

(
echo 
date
/usr/bin/time srun -n $PC ./build/SWE_gnu_release_mpi_fwave.nc -x $X -y $Y -o $OUT/file -c $C
date
ls -lah $OUT/*
rm $OUT/*
) >> results/nc-$SLURM_JOB_NUM_NODES-$PPN.txt 2>&1


if [[ "" == "x" ]] ; then
  # Not sensible for performance reasons right now.
(
echo 
mkfs.esdm -g -l --create --remove --ignore-errors 1>/dev/null 2>&1
date
/usr/bin/time srun -n $PC ./build/SWE_gnu_release_mpi_fwave.nc -x $X -y $Y -o "esdm://out" -c $C
date
find _metadummy/
find /mnt/lustre02/work/bk1040/k202079/_esdm -type f -exec ls -l \{\} \;
find /mnt/lustre01/work/ku0598/k202079/_esdm -type f -exec ls -l \{\} \;
mkfs.esdm -g -l --create --remove --ignore-errors 1>/dev/null 2>&1
) >> results/esdm-nc-$SLURM_JOB_NUM_NODES-$PPN.txt 2>&1
fi


done
done

echo "[OK]"
