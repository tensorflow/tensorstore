# Copyright 2018 Google LLC
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

import distutils
import os
import sys

import setuptools
from setuptools.command import build_ext

DEFAULT_CODE = 'int add(int x, int y) { return x + y; }'


def get_readme():
  with open('setup.rst') as f:
    return f.read()


def get_system_flags(name):
  # TODO(jart): Take quoting into consideration.
  value = distutils.sysconfig.get_config_var(name)
  return frozenset(value.split()) if value else frozenset()


def apply_flags(result, system, flags):
  copy = result[:]
  del result[:]
  known = set()
  known.update(result)
  known.update(system)
  for flag in flags:
    if flag not in known:
      result.append(flag)
      known.add(flag)
  result.extend(copy)  # so Extension() can say -Os if we say -O3


class CcFlags(object):
  def __init__(self, compiler, language, system_copts, system_ldflags, tmp):
    self.compiler = compiler
    self.language = language
    self.system_copts = system_copts
    self.system_ldflags = system_ldflags
    self.tmp = tmp
    self.copts = []
    self.ldflags = []

  def add_if_supported(self, description='', copts=(), ldflags=(),
                       code=DEFAULT_CODE):
    if not (set(copts) - self.system_copts or
            set(ldflags) - self.system_ldflags):
      return True  # no need to check; already in system defaults
    if not description:
      description = ' '.join(sorted(set(tuple(copts) + tuple(ldflags))))
    distutils.log.info('checking %s flags %s', self.language, description)
    if not self._check_flags(copts, ldflags, code):
      distutils.log.info('no')
      distutils.log.info('')
      return False
    self.copts.extend(copts)
    self.ldflags.extend(ldflags)
    distutils.log.info('yes')
    distutils.log.info('')
    return True

  def apply(self, ext):
    if (ext.language == self.language or
        (ext.language == 'c++' and self.language == 'c')):
      apply_flags(ext.extra_compile_args, self.system_copts, self.copts)
      apply_flags(ext.extra_link_args, self.system_ldflags, self.ldflags)

  def _check_flags(self, copts, ldflags, code):
    try:
      suffix = '.cc' if self.language == 'c++' else '.c'
      with open(os.path.join(self.tmp, 'add' + suffix), 'w') as f:
        f.write(code)
        f.flush()
        objs = self.compiler.compile(sources=[f.name],
                                     extra_postargs=list(copts))
      if ldflags:
        self.compiler.link_shared_lib(objects=objs,
                                      output_dir=self.tmp,
                                      output_libname='bin',
                                      extra_postargs=list(ldflags))
      return True
    except (setuptools.distutils.errors.CompileError,
            setuptools.distutils.errors.LinkError):
      return False


class BuildExt(build_ext.build_ext):
  def build_extensions(self):
    distutils.log.info('--------------------')
    distutils.log.info('autoconf tensorstore')
    distutils.log.info('--------------------')

    tmp = os.path.join('build', 'tmp')
    os.makedirs(tmp)

    system_cflags = get_system_flags('CFLAGS')
    system_cxxflags = get_system_flags('CXXFLAGS')
    system_cppflags = get_system_flags('CPPFLAGS')
    system_ldflags = get_system_flags('LDFLAGS')
    cflags = CcFlags(self.compiler, 'c',
                     system_cflags | system_cppflags,
                     system_ldflags,
                     tmp)
    cxxflags = CcFlags(self.compiler, 'c++',
                       system_cflags | system_cxxflags | system_cppflags,
                       system_ldflags,
                       tmp)

    if self.compiler.compiler_type == 'msvc':
      cxxflags.copts += [
          '/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version(),
          '/EHsc',  # allow c++ to have exceptions but not c
      ]

    else:  # unix, gnu, mingw32, etc.
      cflags.copts += ['-DVERSION_INFO="%s"' % self.distribution.get_version()]
      if sys.platform == 'darwin':
        cflags.add_if_supported(copts=['-mmacosx-version-min=10.7'])
        cxxflags.add_if_supported(copts=['-stdlib=libc++'])

      # pybind11 needs c++11 but has smaller footprint with c++14
      if not cxxflags.add_if_supported(
          copts=['-std=c++14'],
          code='''
            // Old Ubuntu14 + Clang5 results in enable_if_t error.
            // Possibly due to old version of libstdc++ but new clang.
            #include <type_traits>
            template <typename T>
            T dubs(std::enable_if_t<std::is_integral<T>::value, T> t) {
              return t * 2;
            }
            int double_add_and(int x, int y) {
              return dubs<int>(x) + dubs<int>(y);
            }
          '''):
        if not cxxflags.add_if_supported(copts=['-std=c++11']):
          raise RuntimeError('Need compiler with C++11 support')

      # symbols hidden by default matters with pybind11
      if cflags.add_if_supported(copts=['-fvisibility=hidden']):
        cxxflags.add_if_supported(copts=['-fvisibility-inlines-hidden'])

      # there shall be no lulz with tensorstore
      cflags.add_if_supported(copts=['-D_FORTIFY_SOURCE=2'])
      cflags.add_if_supported(ldflags=['-Wl,-z,relro,-z,now'])
      if not cflags.add_if_supported(copts=['-fstack-protector-strong']):
        cflags.add_if_supported(copts=['-fstack-protector'])

    # avoid dll hell on gnu/windows
    if self.compiler.compiler_type in ('mingw32', 'cygwin'):
      cflags.add_if_supported(ldflags=['-static-libgcc'])
      cxxflags.add_if_supported(ldflags=['-static-libstdc++'])

    distutils.log.info('-------------------')
    distutils.log.info('compile tensorstore')
    distutils.log.info('-------------------')

    for ext in self.extensions:
      cflags.apply(ext)
      cxxflags.apply(ext)
    build_ext.build_ext.build_extensions(self)


setuptools.setup(
    name='tensorstore',
    version='0.0.1a1',
    description='TensorStore stores tensors',
    long_description=get_readme(),
    url='https://github.com/tensorflow/tensorstore',
    author='Justine Tunney',
    author_email='jart@google.com',
    license='Apache 2.0, BSD-3',
    keywords='tensor sql',
    platforms='any',
    ext_modules=[

        setuptools.Extension(
            name='tensorstore',
            language='c++',
            sources=['tensorstore.cc'],
            include_dirs=['.'],
        ),

    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',  # TensorStore
        'License :: OSI Approved :: BSD License'  # PyBind11
        'License :: OSI Approved',
        'Operating System :: Android',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: iOS',
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
    ],
    cmdclass={'build_ext': BuildExt},
    zip_safe=False,
)
