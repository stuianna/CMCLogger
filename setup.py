import setuptools

with open("README.md","r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "CMCLogger",
    scripts = ['bin/CMCLogger'],
    version = '0.0.1',
    author ="stuianna",
    author_email = "stuiaa@protonmail.com",
    description = "Coin Market Cap Public API Cryptocurrency data logger",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = "https://github.com/stuianna/CMCLogger",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
        ],
    python_requires = '>=3.6',
    install_requires=[
        'pandas',
        'numpy',
        'db-ops',
        'config-checker',
        'python-dateutil',
        'pytz',
        'requests',
        'urllib3',
        'idna',
        'certifi',
        'appdirs',
        'chardet',
        'et-xmlfile',
        'jdcal',
        'openpyxl'
    ],
    )
