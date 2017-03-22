PLUGIN = pip_plugin.py

INSTALL ?= install -p
PYTHON_VERSION=$(shell $(PYTHON) -c \
	'import sys; print(sys.version_info.major)')
PYTHON_LIBDIR=$(shell $(PYTHON) -c \
	'from distutils import sysconfig; print(sysconfig.get_python_lib())')
PLUGINDIR ?= $(PYTHON_LIBDIR)/dnf-plugins

PYTHON ?= python3

install: $(PLUGIN)
	$(INSTALL) -d $(DESTDIR)$(PLUGINDIR)
	$(INSTALL) -m644 $(PLUGIN) $(DESTDIR)$(PLUGINDIR)
	$(PYTHON) -m py_compile $(DESTDIR)$(PLUGINDIR)/$(PLUGIN)
	$(PYTHON) -O -m py_compile $(DESTDIR)$(PLUGINDIR)/$(PLUGIN)

.PHONY: install
