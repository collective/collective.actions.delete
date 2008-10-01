from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='collective.actions.delete',
      version=version,
      description="Action in folder content with confirmation",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='folder delete confirmation',
      author='Ingincollectiveeb',
      author_email='support@ingencollectiveeb.com',
      url='https://svn.plone.org/svn/collective/collective.actions.delete',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
