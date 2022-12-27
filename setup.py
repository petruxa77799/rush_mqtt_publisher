from setuptools import setup, find_packages


setup(
    name='rush_mqtt_sdk',
    description='RUSH MQTT SDK',
    version='0.0.1',
    license='MIT',
    author="Petr Scherbakov",
    author_email='petruxa77799@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/petruxa77799/rush_mqtt_sdk',
    keywords=['MQTT', 'SDK', 'Package', 'Rush'],
    install_requires=[
        'aiohttp'
    ],
)
