from setuptools import setup, find_packages

setup(
    name='cloudpredict',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['click', 'onnxruntime', 'numpy', 'pandas'],
    entry_points={
        'console_scripts': ['cloudpredict=cloudpredict.cli:cli']
    },
)
