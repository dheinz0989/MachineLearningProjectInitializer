from os import environ
from platform import system
import argparse
import re
import subprocess
from pathlib import Path

user = environ['USERNAME'] if 'USERNAME' in list(environ.keys()) else ""
root_dir = Path.cwd().resolve()


class Project_Initializer:
    # def create makefile
    def __init__(self,
                 project_name,
                 user ,
                 e_mail,
                 python_version,
                 main_file,
                 root_dir,
                 dirs,
                 requirements,
                 docker = '',
                 env_name = '',
                 jupyter= '',
                 root_overwrite='n'):
        self.project_name = project_name
        self.user = user
        self.e_mail = e_mail
        self.python_version = python_version
        self.main_file = main_file
        self.root_dir = Path(root_dir)
        self.dirs = dirs
        self.requirements = requirements
        self.docker = docker
        self.env_name = env_name
        self.jupyter = jupyter
        self.root_dir.mkdir(exist_ok=True) if root_overwrite=='y' else self.root_dir.mkdir(exist_ok=False)


    def create_Dockerfile(self,):
        """
        Creates a Dockerfile by inserting the main file, Python version, the user name, user e-mail, an Docker Image specification

        :return:
        """
        image = '-' + self.docker if self.docker else ''
        docker = f"""
FROM python:{self.python_version}{image}
MAINTAINER {self.user} "{self.e_mail}"
RUN apt-get update \
    && apt-get --yes install g++ \
    && apt-get clean
WORKDIR /app
COPY requirements.txt /app
COPY src /app 
RUN pip install -r requirements.txt
CMD ["python", "{self.main_file}" ]
        """
        file = self.root_dir.joinpath('Dockerfile')
        with open(file, 'w') as dfile:
            dfile.write(docker)
        print('Successfully generated a Dockerfile')

    def create_dir(self):
        '''
        Creates all directories provided by the -d paramater

        :return:
        '''
        for d in self.dirs:
            print(f'Create or replacing subdirectory {d}')
            self.root_dir.joinpath(d).mkdir(exist_ok=True)

    def create_requirements(self):
        """
        Creates a requirement files. For each package provided in the package list, it checks the installed version and adds it to it.
        It also checks whether a package is given with a specified version

        :return:
        """
        if self.requirements:
            out = []
            for p in self.requirements:
                if not "==" in p:
                    pip_output = subprocess.run(['pip', 'show', p], stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
                    try:
                        version = re.search('(\d+\.)?(\d+\.)?(\*|\d+)', pip_output).group(0)
                    except AttributeError:
                        version = ''
                    out.append(p + '==' + version)
                else:
                    out.append(p)
            print(f'writing a requirements.txt file with the following entries: {out}')
            file = self.root_dir.joinpath('requirements.txt')
            with open(file, 'w') as require:
                require.write('\n'.join(out))


    def create_Conda_env(self):
        """
        Creates the virtual environment by calling the Anaconda command for this.
        It first checks if the requirements for jupyter notebook/labs have to be added and adds them if so.
        Afterwards, runs the conda virtual environment builder command.

        :return:
        """
        if system()=='Windows':
            print('Creating a virtual environment using Anaconda')
            jupyter_nb = [p for p in self.requirements if 'notebook' in p]
            jupyter_lab = [p for p in self.requirements if 'jupyterlab' in p]
            if not any([jupyter_nb,jupyter_lab]):
                if self.jupyter:
                    jupyter_mapping = {
                        'notebook':'notebook',
                        'lab':'jupyterlab'
                    }
                    self.requirements.append(jupyter_mapping[self.jupyter])
            env_cmd = f"CALL conda create --name {self.env_name} --yes --force {' '.join(self.requirements)}"
            rc = subprocess.run(env_cmd, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
            print(rc)

    def create_jupyter_anaconda(self):
        """
        Creates a batch file which can be used to launch a jupyter lab/notebook instance using the virtual environment created within this repo.

        :return:
        """
        if system() == 'Windows':
            Path('notebooks').mkdir(exist_ok=True)
            if 'CONDA_PREFIX' in list(environ.keys()):
                prefix = environ['CONDA_PREFIX']
            else:
                prefix = ''
                print('Warning: The Anaconda Prefix  was not found in the environment variables. It is used to a '
                      'You therefore need to adapt the jupyter_launcher script. To do this, locate the "activate.bat" '
                      'file in your Anaconda distribution.It is expected to be found via C:\\Users\\`UserName`\\Anaconda3. '
                      'Insert this path to the Scripts\\activate.bat.')

            jupyter_cmd = \
f'''CALL {prefix}\Scripts\\activate.bat
CALL conda activate {self.env_name}
CALL jupyter {self.jupyter}'''
            file = self.root_dir.joinpath('notebooks/launch_jupyter.bat')
            with open(file, 'w') as jupyter:
                jupyter.write(jupyter_cmd)
            print(f"Successfully create a jupyter {self.jupyter} launcher batch file which can be used to activate"
                  f" the '{self.env_name}' environment and work in a jupyter {self.jupyter} environment")

    def create_readme(self):
        """
        Writes a README.md file with inserting the project name, user name, e-mail and the required Python version.
        :return:
        """
        readme_cmd = \
f'''
# {self.project_name}
# Prerequisites
python >= {self.python_version}
# Documentation
Add documentation info here
# Installation

# Usage
# Author
Author of this repo = {self.user}
Contact Information = {self.e_mail}
'''
        file = self.root_dir.joinpath('README.md')
        with open(file, 'w') as readme:
            readme.write(readme_cmd)
        print('Successfully created a README.md file')

    def initialize_git(self):
        """
        git-initializes the directory which was just created.

        :return:
        """
        print('Initializing a git repository')
        commands = ['git init',
                    'git add .',
                    'git commit -m "initial commit"']
        for cmd in commands:
            rc = subprocess.run(cmd.split(), stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
            print(rc)


    def create_main(self):
        """
        Creates a Python main file in the src directory.

        :return:
        """
        file = self.root_dir.joinpath(f'src/{self.main_file}')
        open(file, 'a').close()
        print(f'Created "{self.main_file}" file in src')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Module for creating a Python-based Machine Learning directory.')
    parser.add_argument(
        '--project_name',
        '-n',
        default='My_Project',
        type=str,
        required=False,
        help= 'Indicates the Project Name'
    )
    parser.add_argument(
        "-u",
        "--user",
        type=str,
        required=False,
        default=user,
        help='The author of the directory. Default value is set to the USER Environment variable',
    )
    parser.add_argument(
        "-m",
        "--e_mail",
        type=str,
        required=False,
        default='John.Doe@ibm.com',
        help='The author"s e-mail address for contact information',
    )
    parser.add_argument(
        '--readme',
        '-rd',
        type=str,
        default='y',
        help='If set to y, it creates a first draft of a README.md file'
    )
    parser.add_argument(
        "-v",
        "--python_version",
        type=float,
        required=False,
        default=3.8,
        help='The Python version for a virtual environment'
    )
    parser.add_argument(
        '-r',
        '--root',
        type=str,
        required=False,
        default=root_dir,
        help='The project"s root directory',
    )
    parser.add_argument(
        '-f',
        '--file',
        type=str,
        required=False,
        default='app.py',
        help='The main file',
    )
    parser.add_argument(
        '--docker',
        '-doc',
        type=str,
        required=False,
        default='',
        #choices=['slim',]
        help='A string of the Python Dockerhub for specifiyng the Docker image. Available images can be found here:\nhttps://hub.docker.com/_/python'

    )
    parser.add_argument(
        '--environment',
        '-e',
        type=str,
        required=False,
        default='',
        help='The name of the virtuel environment to be created'
    )
    parser.add_argument(
        '--environment_engine',
        '-eng',
        type=str,
        required=False,
        default='none',
        choices=['anaconda','virtualenv','none'],
        help='Indicates how the virtual environment shall be built. At the moment, virtualenv or Anaconda can be used'
    )
    parser.add_argument(
        '--jupyter',
        '-j',
        type=str,
        default='',
        choices=['notebook','lab'],
        help='Indicates if a jupyter lab or notebook shall be created upon project creation.'
    )
    parser.add_argument(
        '-d',
        '--directories',
        type=str,
        nargs='+',
        required=False,
        default=['cache','data','logs','models','reports','src','docs', 'ims', 'test', 'notebooks', 'admin'],
        help='A list of strings for subdirectories to be created in the the root directory',
    )
    parser.add_argument(
        '-p',
        '--packages',
        type=str,
        nargs='+',
        required=False,
        default=['pandas','numpy'],
        help='A list of all packages written to a requirement file. If you want to add a version number, add the packages followed by "=" and the version.'
             ' If only given the package name, an automated search will retrieve the latest version and write it into the requirement file.'
             'Jupyter notebook and/or labs are automatically if not provided'
    )
    parser.add_argument(
        '--git',
        '-g',
        type=str,
        default='y',
        help='Indicates if a initialization script for git shall be created. y if so'
    )
    parser.add_argument(
        '--overwrite_root',
        '-owr',
        type=str,
        default='n',
        help='Indicates if the root directory file shall be overwritten'
    )

    args = vars(parser.parse_args())
    project_init = Project_Initializer(
        user=args['user'],
        e_mail=args['e_mail'],
        python_version=args['python_version'],
        root_dir = args['root'],
        main_file=args['file'],
        dirs= args['directories'],
        requirements=args['packages'],
        docker=args['docker'],
        project_name=args['project_name'],
        env_name=args['environment'],
        jupyter=args['jupyter'],
        root_overwrite=args['overwrite_root'],
    )
    project_init.create_dir()
    project_init.create_main()
    project_init.create_Dockerfile()
    if args['environment_engine'] == 'anaconda':
        project_init.create_Conda_env()
        project_init.create_jupyter_anaconda()
    project_init.create_requirements()
    if args['readme'] =='y':
        project_init.create_readme()
    if args['git'] == 'y':
        project_init.initialize_git()

