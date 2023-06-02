from setuptools import setup, find_packages

setup(
    name='AIMMee',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'AIMM-simulator',
        'numpy',
        'simpy',
        'matplotlib'
    ],
    python_requires='>=3.8',
)
