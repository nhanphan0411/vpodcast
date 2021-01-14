# vpodcast-demo
web demo for vpodcast project

# How to run?

Change directory:
```
cd vpodcast
```

To prepare this project's environment, we should use miniconda to handle packages.
```pip``` can work but will be stuck at installing ```librosa```. The library relies on ```numba```, installing ```numba``` on Python3 via pip still has conflict and is constantly a pain in the ass. Thus, use conda for better life.  

1. Install miniconda
```
sudo apt-get update
sudo apt-get install bzip2 libxml2-dev
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
rm Miniconda3-latest-Linux-x86_64.sh
source .bashrc
conda install scikit-learn pandas jupyter ipython
```

2. Create and install required environment
```
conda env create -f environment.yml
conda activate vpodcast
```

3. Change directory into app and run the script
```
cd app
python3 main.py
```
