from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='e-cb',
    version='0.1.0',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'flask>=2.0.0',
        'flask-wtf',  # For form handling
        'spacy>=3.5.0',
        'pyyaml>=6.0.0',
        # Any other dependencies
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pre-commit>=2.20.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'isort>=5.10.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'chatbot-framework=web.app:main',
        ],
    },
    author='Hoang Khanh Duy',
    author_email='duyhk.21it@vku.udn.vn',
    description='A very weird framework that help create/implementation chatbot',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/NickDuyH2K3/E-CB',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
)