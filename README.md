dnf-plugin-pip
==============

A plugin for [DNF] that does can be used to manipulate Python packages.

Installation
------------

    # make install

Example Usage
-------------

To install PyPi packages from a development project.

    # dnf pip install -r requirements_dev.txt

To uninstall PyPi packages listed in a Python requirements file.

    # dnf pip uninstall -r requirements.txt

You can also specify what version of Python to (un)install for.

    # dnf pip --python 2.7 install -r requirements.txt

PyPi packages don't have to be in a requirements.txt format...

    # dnf pip install scipy pyYAML

...works just as well.

License
-------

See [LICENSE]

[DNF]: https://github.com/rpm-software-management/dnf
[LICENSE]: LICENSE
