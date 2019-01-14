from setuptools import find_packages, setup

with open('requirements.txt') as f:
    install_reqs = f.read().splitlines()

with open('test_requirements.txt') as f:
    testing_reqs = f.read().splitlines()

setup(
    name='dcu-validator-api',
    version='1.0',
    author='DCU',
    author_email='dcueng@godaddy.com',
    description='REST API for periodically validating DCU tickets',
    url='https://github.secureserver.net/ITSecurity/dcu-validator',
    packages=find_packages(exclude=['tests']),
    install_requires=install_reqs,
    tests_require=testing_reqs,
    test_suite='nose.collector',
    classifiers=[
        'Programming Language :: Python :: 2.7'
    ]
)
