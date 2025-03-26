from setuptools import setup, find_packages

setup(
    name='chatbot-framework',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-wtf',  # If you're using WTForms
        'spacy>=3.5.0',  # Add SpaCy dependency
        # Other dependencies
    ],
    entry_points={
        'console_scripts': [
            'chatbot-framework=web.app:main',
        ],
    },
    author='Your Name',
    description='A flexible chatbot framework',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)