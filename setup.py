from setuptools import setup


try:
    setup (
        name='anylog_api',
        version="beta",
        description='AnyLog API tool',
        url='https://anylog.co',
        author='AnyLog Team',
        author_email='info@anylog.co',
        license='AnyLog, Co. -  See License Agreement',
        install_requires=[
            'requests>=2.27.1'
        ],
        packages=['pyapi'],
        classifiers=[
            'Development Status :: 1 - Planning',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9'
        ]
    )
except Exception as e:
    print(f"Failed to build AnyLog (Error: {e})")





