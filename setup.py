"""
setup.py
"""

from setuptools import setup, find_packages

# load version
with open('logos_pipe_ocr/__version__.py', 'r') as f:
    version = f.read().strip().split('=')[1].replace('"', '').replace("'", '')

# install_requires is loaded from requirements.txt
with open('requirements.txt', 'r', encoding='utf-8-sig') as f:
    install_requires = f.read().splitlines()

setup(
    name='logos_pipe_ocr',
    version=version,
    author='insightercorperation',
    author_email='ylahn@insighter.co.kr',
    description='Logos-pipe-ocr is a data quality assessment library for LLM OCR\'s processed data.',
    packages=find_packages(),
    install_requires=install_requires,
    url='https://github.com/insightercorperation/logos-pipe-ocr-v1.git',
    # source code root
    entry_points={
        'console_scripts': [
            'logos_pipe_ocr=logos_pipe_ocr.main:main',
        ],
    },
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
