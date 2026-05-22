#!/bin/bash
##------------------------ Start job description -----------------------

#SBATCH --partition=standard
#SBATCH --job-name=pyhope_CRM_g3
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --time=12:00:00
#SBATCH -e LOG/err-%j.log
#SBATCH -o LOG/out-%j.log

##------------------------ End job description ------------------------

module purge
source "$HOME/venvs/pyhope310/bin/activate"
module load libGLU
module load Python/3.10.4-GCCcore-11.3.0

# # OpenMP / threading configuration (Uncomment for multi-threading)
# export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
# export OMP_SCHEDULE=guided
# export OMP_PROC_BIND=close
# export OMP_PLACES=cores

# # If using MKL/OpenBLAS/NumExpr (common in Python), limit threads as well:
# export MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK}
# export OPENBLAS_NUM_THREADS=${SLURM_CPUS_PER_TASK}
# export NUMEXPR_NUM_THREADS=${SLURM_CPUS_PER_TASK}

# echo "##########################################################################"
# echo "# Running with ${SLURM_NTASKS} task and ${SLURM_CPUS_PER_TASK} cpus/task"
# echo "# OMP_NUM_THREADS=${OMP_NUM_THREADS}"
# echo "# On nodes ${SLURM_JOB_NODELIST}"
# echo "##########################################################################"

# Execute PyHOPE with the specific initialization file
srun pyhope parameter.ini
