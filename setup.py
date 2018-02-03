from setuptools import setup

setup(
    name='gdaxtrader',
    version='0.1a1',
    homepage='https://github.com/bmbouter/gdaxtrader/',
    description='Automated and manual cryptocurrency trading on the GDAX exchange without fees',
    url='http://github.com/bmbouter/gdaxtrader',
    author='Brian Bouterse',
    author_email='bmbouter@gmail.com',
    license='GPLv3',
    packages=['gdaxtrader'],
    install_requires=[
        'Django',
        'gdax',
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
