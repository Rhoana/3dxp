source new-modules.sh
module load python/2.7.11-fasrc01

# Check the virtual enviroment
VENV_NAME="3DXP"
VENV_INFO=`conda env list | grep "^$VENV_NAME\s"`

# Get the directory of the main repository
REPO=`git rev-parse --show-toplevel`

# Make the virtual environment if needed
if [ -z "$VENV_INFO" ]; then
    echo "Making virtual environment $VENV_NAME"
    conda create -n $VENV_NAME --clone="$PYTHON_HOME"
    source activate $VENV_NAME
    conda remove scikit-image
    pip install -r $REPO/requirements.txt
fi
