# coding=utf-8
from setuptools import setup

setup(
    name="TcTube",
    version="0.3.1",
    description="網頁版 線上會員訓練系統",
    author="TCC",
    author_email="john987john987@gmail.com",
    license="MIT",
    url="https://github.com/TCCinTaiwan/TcTube",
    install_requires=[
        "Flask==0.10.1",
        "Flask-Login==0.3.2",
        "Flask-SQLAlchemy==2.1",
        "Flask-Compress==1.3.0",
        "Flask-SocketIO==2.6",
        "WTForms==2.1",
        "Pygments==2.0.2",
        "colorama==0.3.7",
        "numpy==1.11.1",
        "requests==2.8.1",
        "eventlet==0.17.4",
    ],
)