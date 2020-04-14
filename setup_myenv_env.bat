@echo off
conda create --name myenv --yes
conda activate myenv
FOR /F "delims=~" %%f in (requirements.txt) DO conda install --yes "%%f" || conda install --yes -c conda-forge "%%f" || pip install "%%f"
echo All requirements have been installed
echo You can safely delete this file now
cmd /K