from setuptools import setup, find_packages

setup(
    name='asaps',
    version='1.0.0',
    description='',
    packages=find_packages(exclude=['tests']),
    author='Eric Hanson',
    author_email='ehanson@mit.edu',
    install_requires=[
        'archivessnake',
        'click',
        'jsonpatch',
        'jsonpointer',
        'structlog',
    ],
    entry_points={
        'console_scripts': [
            'asaps=asaps.cli:main',
        ]
    },
    python_requires='>=3.8',
)
