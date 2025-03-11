# setup.py
from setuptools import setup, find_packages

setup(
    name='loki-django-logger',
    version='1.0.2',  # Increment version after improvements
    description='Asynchronous Loki logger for Django applications',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Irwin Rex',
    author_email='irwinrex.a@gmail.com',
    url='https://github.com/irwinrex/loki-django-logger',
    packages=find_packages(),
    install_requires=[
        'Django>=4.0',
        'httpx>=0.23.0,<1.0.0'  # Pin version range for compatibility
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Topic :: System :: Logging',
    ],
    keywords='django loki logger async',
    python_requires='>=3.10',
    include_package_data=True,
)
