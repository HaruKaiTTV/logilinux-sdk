from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
import sys
import os

try:
    import pybind11
    pybind11_include = pybind11.get_include()
except ImportError:
    pybind11_include = ''

# Native C++ extension module
ext_modules = [
    Extension(
        '_logilinux_native',  # Internal module name
        sources=['src/bindings.cpp'],
        include_dirs=[
            pybind11_include,
            'logilinux-driver/lib/include',
            'logilinux-driver/lib/src',  # For internal device headers
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
    description='Python SDK for LogiLinux - Logitech device library for Linux',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    
    # Python packages
    packages=find_packages(exclude=['tests', 'examples']),
    
    # C++ extension
    ext_modules=ext_modules,
    
    # Dependencies
    install_requires=[
        'pybind11>=2.6.0',
        'Pillow>=9.0.0',  # For image rendering in PluginCommand
    ],
    setup_requires=['pybind11>=2.6.0'],
    
    python_requires='>=3.7',
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: C++',
        'Topic :: System :: Hardware :: Hardware Drivers',
    ],
    
    keywords='logitech mx creative console dialpad keypad input device',
)

