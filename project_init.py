from os import makedirs, getcwd, environ
import argparse
from packaging import version
import requests
from pathlib import Path

user = environ['USERNAME'] if 'USERNAME' in list(environ.keys()) else ""
root_dir = Path.cwd().resolve()


class Project_Initializer:
    # def create makefile
    def __init__(self,
                 user ,
                 e_mail,
                 python_version,
                 main_file,
                 root_dir,
                 dirs,
                 requirements,
                 docker = True,
                 readme = True,
                 conda_env = True):
        self.user = user
        self.e_mail = e_mail
        self.python_version = python_version
        self.main_file = main_file
        self.root_dir = root_dir
        self.dirs = dirs
        self.requirements = requirements
        self.docker = docker
        self.readme = readme
        self.conda_env = conda_env


    def create_dir(self):
        '''
        Creates all directories mentioned in the .dirs attribute

        :return:
        '''
        for d in self.dirs:
            print(f'Create or replacing subdirectory {d}')
            Path(d).mkdir(exist_ok=True)

    def parse_package_args(self):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Module for creating a Python-based Machine Learning directory.')
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
        '-d',
        '--dirs',
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
    args = vars(parser.parse_args())
    project_init = Project_Initializer(
        user=args['user'],
        e_mail=args['e_mail'],
        python_version=args['python_version'],
        root_dir = args['root'],
        main_file=args['file'],
        dirs= args['dirs'],
        requirements=args['packages']
    )
    print(args)
    print(project_init)
    project_init.create_dir()
    project_init.parse_package_args()
