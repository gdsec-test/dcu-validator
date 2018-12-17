from pip.req import parse_requirements
from setuptools import find_packages, setup

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session=False)
test_requirements = parse_requirements('test_requirements.txt', session=False)

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]
test_reqs = [str(ir.req) for ir in test_requirements]

setup(
    name='dcu-validator-scheduler',
    version='1.0',
    description='gRPC service for periodically validating DCU tickets',
    author='DCU-ENG',
    author_email='dcueng@godaddy.com',
    url='https://github.secureserver.net/ITSecurity/dcu-validator',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=reqs,
    tests_require=test_reqs,
    test_suite="nose.collector")
