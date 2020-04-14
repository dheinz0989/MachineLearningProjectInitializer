from os import environ
from platform import system
import argparse
from packaging import version
import requests
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
                 readme = 'y',
                 git = 'y',
                 env_builder = '',
                 jupyter= ''):
        self.project_name = project_name
        self.user = user
        self.e_mail = e_mail
        self.python_version = python_version
        self.main_file = main_file
        self.root_dir = root_dir
        self.dirs = dirs
        self.requirements = requirements
        self.docker = docker
        self.env_name = env_name
        self.readme = readme
        self.git = git
        self.env_builder = env_builder
        self.jupyter = jupyter

    def create_Dockerfile(self,):
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
        with open('Dockerfile', 'w') as dfile:
            dfile.write(docker)
        print('Successfully generated a Dockerfile')

    def create_dir(self):
        '''
        Creates all directories mentioned in the .dirs attribute

        :return:
        '''
        for d in self.dirs:
            print(f'Create or replacing subdirectory {d}')
            Path(d).mkdir(exist_ok=True)

    def create_requirements(self):
        if self.requirements:
            packages_with_version = [f for f in self.requirements if '==' in f]
            packages_without_version = self.list_diff(self.requirements,packages_with_version)
            packages = [package + '=='+self.get_latest_version(package) for package in packages_without_version] + packages_with_version
            print(f'writing a requirements.txt file with the following entries: {packages}')
            with open('requirements.txt', 'w') as require:
                require.write('\n'.join(packages))
    # add git init
    @staticmethod
    def list_diff(a,b):
        '''
        Returns a list of all entries which are not found in both lists.

        :param a:
        :param b:
        :return:
        '''
        return list(set(a).symmetric_difference(set(b)))

    @staticmethod
    def get_latest_version(package):
        '''
        Retrieves the package's latest version found in the pypi Homepage which is used by "pip install"

        :param package:
        :return:
        '''
        print(f'Retrieving latest version for package {package}')
        pypi_url = f"https://pypi.python.org/pypi/{package}/json"
        resp = requests.get(pypi_url)
        try:
            versions = list(resp.json()["releases"].keys())
            latest_version = str(max([version.parse(v) for v in versions]))
            return latest_version
        except Exception:
            print(f'Package {package} was not found at pypi. You need to add the version number in the requirement.txt file afterwards.')
            return

    def create_env(self):
       if not self.env_builder:
            return
       if system()=='Windows':
           if self.env_builder=='anaconda':
               env_cmd = \
f'''@echo off
conda create --name {self.env_name} --yes
conda activate {self.env_name}
FOR /F "delims=~" %%f in (requirements.txt) DO conda install --yes "%%f" || conda install --yes -c conda-forge "%%f" || pip install "%%f"
echo All requirements have been installed
echo You can safely delete this file now
cmd /K'''

           elif self.env_builder=='virtualenv':
               if 'USERPROFILE' in list(environ.keys()):
                   prefix = environ['USERPROFILE']
               else:
                   prefix = ''
                   print('Warning: The User Profile prefix was not found in the enviornment variables. '
                         'The environment setup script needs to be adapted. To do this, locate the "activate.bat" file in your virtual environ setup.')
               env_cmd = \
f'''pip install virtualenv
virtualenv {self.env_name}
{prefix}\\{self.env_name}\\Scripts\\activate.bat
FOR /F "delims=~" %%f in (requirements.txt) DO pip install "%%f"
echo All requirements have been installed
echo You can safely delete this file now
cmd /K'''
           with open(f'setup_{self.env_name}_env.bat', 'w') as env_setup:
               env_setup.write(env_cmd)
           print(f'Successfully create an environment setup script for {self.env_name}. Run it once to create the environment. Afterwards, it can safely be deleted')

    def create_jupyter(self):
        if not self.jupyter:
            return
        Path('notebooks').mkdir(exist_ok=True)
        if system() == 'Windows':
            if self.env_builder == 'anaconda':
                jupyter_cmd = \
f'''conda activate {self.env_name}
jupyter {self.jupyter}'''
            elif self.env_builder == 'virtualenv':
                if 'USERPROFILE' in list(environ.keys()):
                    prefix = environ['USERPROFILE']
                else:
                    prefix = ''
                    print('Warning: The User Profile prefix was not found in the enviornment variables. '
                          'The jupyter setup script needs to be adapted. To do provide the full path to locate the "activate.bat" file in your virtual directory.')
                jupyter_cmd = \
f'''{prefix}\\{self.env_name}\\Scripts\\activate.bat
jupyter {self.jupyter}'''
        with open('notebooks/launch_jupyter.bat', 'w') as jupyter:
            jupyter.write(jupyter_cmd)
        print(f"Successfully create a jupyter {self.jupyter} launcher batch file which can be used to activate"
              f" the '{self.env_name}' environment and work in a jupyter {self.jupyter} environment")


    def create_readme(self):
        if self.readme =='y':
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
            with open('README.md', 'w') as readme:
                readme.write(readme_cmd)
            print('Successfully created a README.md file')

    def create_git(self):
        if self.git == 'y':
            git_cmd = \
f'''git init
git add .
git commit -m "initial commit"
echo You can safely delete this file now
cmd /K
            '''
            with open('init_git.bat','w') as file:
                file.write(git_cmd)
            print('Created a "init_git.bat" batch file which can be called once. It can safely deleted afterwards')


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
        default='',
        choices=['anaconda','virtualenv'],
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
        help='A list of all packages written to a requirement file. If you want to add a version number, add the packages followed by "==" and the version.'
             ' If only given the package name, an automated search will retrieve the latest version and write it into the requirement file.'
    )
    parser.add_argument(
        '--git',
        '-g',
        type=str,
        default='y',
        help='Indicates if a initialization script for git shall be created. y if so'
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
        git=args['git'],
        env_name=args['environment'],
        env_builder=args['environment_engine'],
        jupyter=args['jupyter']
    )
    project_init.create_dir()
    project_init.create_requirements()
    project_init.create_Dockerfile()
    project_init.create_env()
    project_init.create_jupyter()
    project_init.create_git()
    project_init.create_readme()
