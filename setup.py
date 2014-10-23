#! /usr/bin/env python

from setuptools import setup

setup(name="iwantaserver",
      version="0.0.0",
      description="Site to hand out servers like candy",
      author="Brian Curtin",
      author_email="brian@python.org",
      packages=["iwantaserver"],
      scripts=["givemeaserver.py"],
      include_package_data=True,
      zip_safe=False
     )
