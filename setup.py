from setuptools import setup,find_packages

setup(
    name='flat-mq',
    version='0.1.2',
    description='',
    author='Charlie Hsieh',
    author_email='oe327188@gmail.com',
    python_requires=">=3.9",
    url='https://github.com/mingyen298/flat-mq',
    packages=find_packages(exclude=["tests*"]), 
    install_requires=[
        "asyncio==3.4.3",
        "flat-mq-client @ git+https://github.com/mingyen298/flat-mq-client.git@f1772518a759daa1592da254952ae5afa513e865",
        "pydantic==2.6.4"

    ],  
)
