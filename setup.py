import os
import sys
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

VERSION = os.environ.get('VERSION', '0.121.X')
RELEASE = os.environ.get('RELEASE', '.dev')

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# don't allow setup.py to be run from any path
#os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open('requirements.txt', 'r') as f:
    required = f.read().splitlines()

with open('test_requirements.txt', 'r') as f:
    test_required = f.read().splitlines()

def prepend_find_packages(*roots):
    ''' Recursively traverse nested packages under the root directories
    '''
    packages = []
    
    for root in roots:
        packages += [root]
        packages += [root + '.' + s for s in find_packages(root)]
        
    return packages

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name='blue_sky_test',
    version='%s%s' % (VERSION, RELEASE),
    packages=prepend_find_packages('blue_sky'),
    package_data={'': ['*.conf', '*.cfg', '*.json', '*.env', '*.sh', '*.txt', 'Makefile'] },
    include_package_data=True,
    license='Allen Institute Software License',
    description='Blue Sky Workflow Test',
    long_description=README,
    url='https://github.com/AllenInstitute',
    author='Nathan Sjoquist',
    author_email='nathans@alleninstitute.org',
    install_requires = required,
    tests_require=test_required,
    setup_requires=[
        'flake8'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: Allen Institute Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    cmdclass = {'test': PyTest},
)
