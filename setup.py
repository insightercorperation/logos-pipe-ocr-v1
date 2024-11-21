"""
setup.py
"""

from setuptools import setup, find_packages

# install_requires
with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

with open('logos-pipe-ocr-v1/__version__.py', 'r') as f:
    version = f.read().strip().split('=')[1].replace('"', '').replace("'", '')

setup(
    name='logos-pipe-ocr',
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
            'logos-pipe-ocr=logos-pipe-ocr.main:main',
        ],
    },
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
