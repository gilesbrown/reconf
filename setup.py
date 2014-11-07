from setuptools import setup

version = '0.1.1'

setup(
    name='reconf',
    description="Reloadable configuration settings.",
    version=version,
    author='Giles Brown',
    author_email='giles_brown@hotmail.com',
    url='http://github.com/gilesbrown/reconf',
    download_url = 'http://github.com/gilesbrown/reconf/tarball/' + version,
    license='BSD',
    packages=['reconf'],
    install_requires=[
        'six>=0.1.8',
    ],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.3',
    ),
)
