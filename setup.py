from setuptools import setup, find_packages

setup(
    name='ArchivesSpace API Python Scripts',
    version='1.0.0',
    description='',
    packages=find_packages(exclude=['tests']),
    author='Eric Hanson',
    author_email='ehanson@mit.edu',
    install_requires=[
        'attrs',
        'click',
        'archivessnake'
    ],
    python_requires='>=3.7.1',
)
