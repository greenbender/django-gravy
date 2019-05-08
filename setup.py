import os
from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name='django-gravy',
    version='0.3.2',
    packages=find_packages(),

    # only install the most common requirements
    install_requires = [
        'django-betterforms',
        'python-magic',
        'pyfifo',
        'pycrypto',
        'beautifulsoup4',
        'jsonfield',
    ],
    include_package_data=True,
    license='BSD License',
    description='Reusable extras for Django (the gravy).',
    long_description=README,
    author='greenbender',
    author_email='byron.platt@gmail.com',
    url='https://github.com/greenbender/django-gravy',
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
