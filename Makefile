name = dstat-plugins

prefix = /usr
sysconfdir = /etc
bindir = $(prefix)/bin
datadir = $(prefix)/share
mandir = $(datadir)/man

.PHONY: all install clean

all:
	@echo "Nothing to be build."

install:
	install -Dp -m0644 plugins/dstat_*.py $(DESTDIR)$(datadir)/dstat/

clean:
	rm -f plugins/*.pyc
