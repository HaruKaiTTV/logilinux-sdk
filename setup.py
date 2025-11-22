from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import os

class get_pybind_include(object):
    def __str__(self):
        import pybind11
        return pybind11.get_include()

ext_modules = [
    Extension(
        'logilinux',
        sources=['src/bindings.cpp'],
        include_dirs=[
            str(get_pybind_include()),
            'logilinux-driver/lib/include',
        ],
        library_dirs=[
            'logilinux-driver/build/lib',
        ],
        libraries=['logilinux'],
        language='c++',
        extra_compile_args=['-std=c++17'],
    ),
]

setup(
    name='logilinux',
    version='0.1.0',
    author='ron0studios',
    description='Python bindings for LogiLinux - Logitech device library for Linux',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    ext_modules=ext_modules,
    packages=['python'],
    package_dir={'python': 'python'},
    install_requires=['pybind11>=2.6.0'],
    setup_requires=['pybind11>=2.6.0'],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: C++',
    ],
)
