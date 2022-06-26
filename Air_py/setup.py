from setuptools import setup

setup(
    name='air_py',
    version='0.0.1',
    install_requires=[
        'requests',
        'importlib-metadata; python_version == "3.8"',
        "adafruit-circuitpython-dht", 
        "libgpiod2"
    ],
)