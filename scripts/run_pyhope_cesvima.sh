#!/bin/bash
# ==============================================================================
# Script: run_pyhope_cesvima.sh
# Author: Mateo Guamán Cueva
# Description: HPC environment initialization and execution script for PyHOPE
#              on the CESVIMA supercomputing cluster.
# ==============================================================================

echo "Initializing HPC environment for PyHOPE..."

# 1. Load required modules (Python and GLU libraries)
module load Python/3.10.4-GCCcore-11.3.0
module load libGLU/9.0.2-GCCcore-11.3.0

# 2. Virtual environment setup and activation
# (Assuming the venv is already created. If not, uncomment the next line)
# python3.10 -m venv ~/venvs/pyhope310

source /venvs/pyhope310/bin/activate
echo "Virtual environment activated successfully."

# 3. Execute PyHOPE with the specified configuration file
# Usage: ./run_pyhope_cesvima.sh <parameter_file.ini>
# If no file is passed, it defaults to 'parameter.ini'
PARAM_FILE=${1:-parameter.ini}

echo "Running PyHOPE with configuration: $PARAM_FILE"
pyhope $PARAM_FILE

echo "Execution finished."
# ==============================================================================
