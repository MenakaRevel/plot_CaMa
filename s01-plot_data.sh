#! /bin/bash
########################
#*** PBS seeting when needed
#PBS -q F10
#PBS -l select=1:ncpus=10:mem=40gb
#PBS -j oe
#PBS -m bea
#PBS -M your@email.com
#PBS -V
#PBS -N cal_max_dis

# #
# # cd $PBS_O_WORKDIR
# cd "/work/a06/menaka/plot_CaMa"

# USER=`whoami`

# # 
# # NCPUS=`cat $PBS_NODEFILE | wc -l`
# NCPUS=10
# export OMP_NUM_THREADS=$NCPUS

dataname="./dat/outflw2000.bin"
mapname="GBM_15min"
CaMa_dir="/work/a07/uddin/Cama-Flood/CaMa-Flood_v4"
rivnums="./dat/rivnum_${mapname}.bin"
figname="mean_outflow"

mkdir -p ./fig

python ./src/map_data.py $dataname $mapname $CaMa_dir $rivnums $figname  