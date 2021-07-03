
from setuptools import setup

setup(
    name="aws-instance-tool",
    version="0.1.0",

    description="A simple tool for managing AWS EC2 instances",
    author="Bradley Worley",
    author_email="geekysuavo@gmail.com",

    license="MIT",

    packages=["aws_instance"],
    install_requires=["Click"],
    requires=[
        "click",
        "pyyaml",
        "boto3",
        "botocore",
    ],
    entry_points={
        "console_scripts": [
            "aws-instance = aws_instance.frontend:main",
        ],
    },
)
