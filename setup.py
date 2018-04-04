from setuptools import setup

setup(name='studyExtraction',
      version='0.1',
      licence='GNU GPLv3',
      description='Script to filter and extract data from the eTox Vitic database.',
      url='https://github.com/phi-grib/studyExtraction',
      download_url='https://github.com/phi-grib/studyExtraction.git',
      author='Elisabet Gregori and Ignacio Pasamontes',
      author_email='elisabet.gregori@upf.edu',
      packages=['extract'],
      package_data={
        'extract': ['data/*'],
        },
      scripts=['src/extract.py']
    )
