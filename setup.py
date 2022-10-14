from setuptools import setup, find_packages

setup(
    name='py-database-cli',
    version='0.1.0',
    packages=find_packages(exclude=["tests"]),
    url='https://github.com/ricekab/py-database-cli',
    license='MIT',
    author='Kevin CY Tang',
    author_email='contact@kevinchiyantang.com',
    keywords='sqlalchemy cli commandline interface database db crud inspect',
    description="Commandline tool for basic database CRUD operations which is "
                "(mostly) back-end agnostic.",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    install_requires=['SQLAlchemy', 'click'],
    tests_require=[],
    python_requires='>=3.7',
    entry_points='''
    [console_scripts]
    pydbcli=pydatabasecli.cli:cli
    ''',
)
