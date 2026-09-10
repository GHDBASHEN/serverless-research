from setuptools import setup, find_packages

setup(
    name='cloudpredict',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pandas', 
        'joblib', 
        'scikit-learn', 
        'lightgbm', 
        'xgboost', 
        'tabulate'
    ],
    entry_points={
        'console_scripts': ['cloudpredict=cloudpredict.cli:main']
    },
)
