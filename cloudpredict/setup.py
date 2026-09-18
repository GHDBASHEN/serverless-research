from setuptools import setup, find_packages

setup(
    name='cloudpredict',
    version='0.2.5',
    description='Cross-platform serverless performance & cost predictor (AWS / Azure / GCP)',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'cloudpredict': ['models/*.pkl'],
    },
    install_requires=[
        'pandas',
        'joblib',
        'scikit-learn==1.5.0',  # pinned: shipped .pkl models were trained on this version
        'lightgbm',
        'xgboost==1.7.6',       # pinned: prevents UserWarning about older serialized model
        'tabulate'
    ],
    entry_points={
        'console_scripts': ['cloudpredict=cloudpredict.cli:main']
    },
)
