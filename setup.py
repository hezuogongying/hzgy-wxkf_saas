# -*- coding: utf-8 -*-
"""Setup script for wxkf_saas"""

from setuptools import setup, find_packages

setup(
    name="wxkf_saas",
    version="1.0.0",
    description="微信客服SaaS服务平台",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "asyncmy",
        "pymysql",
        "redis",
        "httpx",
        "python-multipart",
    ],
    python_requires=">=3.8",
)