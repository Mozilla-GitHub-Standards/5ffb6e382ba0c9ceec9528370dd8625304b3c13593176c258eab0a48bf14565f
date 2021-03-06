# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
from setuptools import setup, find_packages
import os
import re


install_requires = ['SQLALchemy', 'unittest2', 'mozsvc', 'cornice',
                    'metlog-py']

entry_points = """
[paste.app_factory]
main = aitc:main

[paste.app_install]
main = paste.script.appinstall:Installer
"""

# extracting the version number from the .spec file
here = os.path.dirname(__file__)
spec = os.path.join(here, 'AITC.spec')
with open(spec) as f:
    spec = f.read()

_VERSION = re.compile('^%define version (.*)$', re.M)
version = _VERSION.findall(spec)[0]


setup(name='AITC',
      version=version,
      packages=find_packages(),
      install_requires=install_requires,
      entry_points=entry_points,
      license='MPLv2.0',
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        ],
      test_suite="aitc",
      package_data={
          "aitc.tests": ["*.ini"],
      },
      include_package_data=True,
)
