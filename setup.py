from setuptools import setup, find_packages

setup(
    name='quisby',
    version='0.0.1',
    description='Process benchmark results and automatically add to Google Sheets',
    author='Soumya Sinha',
    author_email='sinhasoumya97@gmail.com',
    url='https://github.com/redhat-performance/quisby',
    long_description=open("README.md").read(),
    packages=find_packages(),
    install_requires=[
        'boto3==1.17.97',
        'botocore==1.20.97',
        'bs4==0.0.1',
        'google-api-core==1.30.0',
        'google-api-python-client==2.9.0',
        'google-api==0.1.12',
        'google-auth-httplib2==0.1.0',
        'google-auth-oauthlib==0.4.4',
        'google-auth==1.31.0',
        'googleapis-common-protos==1.53.0',
        'oauthlib==3.1.1',
        'requests-oauthlib==1.3.0',
        'requests==2.32.4',
        'scipy==1.11.4',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GPL-3.0 License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    entry_points={
        "console_scripts": [
            "quisby = quisby.quisby:main",
        ]
    },
)
