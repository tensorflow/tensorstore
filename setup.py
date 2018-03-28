# Copyright 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import setuptools


def get_readme():
  with open('setup.rst') as f:
    return f.read()


setuptools.setup(
    name='tensorstore',
    version='0.0.1a1',
    description='TensorStore stores tensors',
    long_description=get_readme(),
    url='https://github.com/tensorflow/tensorstore',
    author='Google Inc.',
    author_email='opensource@google.com',
    license='Apache 2.0',
    keywords='tensor sql',
    platforms='any',
    packages=setuptools.find_packages(exclude=["*._test.*"]),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'License :: OSI Approved',
        'Programming Language :: C',
        'Programming Language :: C++',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: SQL',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Database',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries',
    ])
