# MachineLearningProjectInitializer
This short module has only one function to use: it initializes a directory and common files found in Machine Learning Projects. Based on the options, the following commands are possible:
- create a common Machine Learning project directory <br />
- it can add README.md files and initialize git <br />
- it can add a Dockerfile <br />
- it can create a virtual Environment. Currently, only the [Anaconda](https://www.anaconda.com/) virtual environment creator is implemented.  <br />
- for Windows user, a batch script can be added to activate the virtual environment and open a [Jupyter](https://jupyter.org/) lab/notebook instance using the respective virtualenvironment Interpreter.  <br />
- it can add a requirement.txt files (for instance, used by Docker) <br />
- It can also create an "app.y" found in the src directory. <br />

Myrepo/ <br />
├── admin/ <br />
├── cache/ <br />
├── data/ <br />
├── Dockerfile <br />
├── docs/ <br />
├── ims/ <br />
├── logs/ <br />
├── models/ <br />
├── notebooks/ <br />
│   └── launch_jupyter.bat <br />
├── README.md <br />
├── reports/ <br /> 
├── requirements.txt <br />
├── src/ <br />
│   └── app.py <br />
└── test/ <br />

# Prerequisits
The source code is written in [Python 3.8](https://www.python.org/). It use the standard libraries *pathlib*, *platform*, *os*, *re*, *subprocess* and *argparse*.
Furthermore, for some of the functionalities, external commands are necessary: 
- for using the Anaconda environment builder, ensure that the [Anaconda Command line](https://docs.anaconda.com/anaconda/user-guide/getting-started/) is installed and added to the system path variables. <br />
- for using git initiliazer, ensure that [git](https://git-scm.com/) is installed and added to the system path variables

# Installation
You can clone this repository by running:
	
	git clone https://github.com/dheinz0989/MachineLearningProjectInitializer

# Usage
An example call is found in the batch file in this repo. It initializes a repository with the following parameter:
User: Dominik Heinz, -e-mail: dheinz0989@gmail.com, create ReadME, Python version: 3.8, main file: app.py, root directory: C:\Daten\Trainings\Myrepo, environment: myenvironment, environment builder: anaconda, jupyter: lab, Initialize git, packages: numpy; pandas; matplotlib, overwrite existing directory

```
python project_init.py -n MyMachineLearningProject ^
 -u "Dominik Heinz" ^
 -m "dheinz0989@gmail.com" ^
 -rd y ^
 -v 3.8 ^
 -f app.py ^
 -r C:\Daten\Trainings\Myrepo ^
 -e myenvironment ^
 -eng anaconda ^
 -j lab ^
 -g y ^
 -p numpy pandas matplotlib ^
 -owr y
```

# To Do
This repository has several things which are not implemented yet. Amongs others, the following implementation are planned:
1. Implement the virtualenv builder
2. Add common files like makefile, docker-compose, etc.
3. Implement for Unix/Mac systems