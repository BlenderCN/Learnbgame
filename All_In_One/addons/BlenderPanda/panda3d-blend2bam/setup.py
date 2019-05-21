from setuptools import setup


def readme():
    with open('README.md') as readme_file:
        return readme_file.read()


setup(
    name='panda3d-blend2bam',
    version='0.6',
    description='A tool to convert Blender blend files to Panda3D BAM files',
    long_description=readme(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='panda3d gamedev',
    url='https://github.com/Moguri/panda3d-blend2bam',
    author='Mitchell Stokes',
    license='MIT',
    packages=['blend2bam'],
    include_package_data=True,
    install_requires=[
        'panda3d',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest==4.1.*',
        'pylint==2.2.*',
        'pytest-pylint',
    ],
    entry_points={
        'console_scripts':[
            'blend2bam=blend2bam.cli:main',
        ],
    },
)
