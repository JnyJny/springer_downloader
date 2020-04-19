# demo/Makefile - create SVG animations to demonstrate
#                 how to use the springer downloading tool

SPRINGER= springer

TARGETS= default_catalogs_demo list_demo downloading_demo

PLAY= ./demo.py "$1"

RECORD= termtosvg $1 -g 100x$2 -m 10 -M 500 -t window_frame

# Script items need a terminating semi-colon (except for last)

DEFAULT_CATALOGS_SCRIPT =$(SPRINGER) get-default-catalog;
DEFAULT_CATALOGS_SCRIPT+=$(SPRINGER) -L de set-default-catalog;
DEFAULT_CATALOGS_SCRIPT+=$(SPRINGER) list catalog;
DEFAULT_CATALOGS_SCRIPT+=$(SPRINGER) -L de -T med set-default-catalog;
DEFAULT_CATALOGS_SCRIPT+=$(SPRINGER) list catalog;
DEFAULT_CATALOGS_SCRIPT+=$(SPRINGER) -L en -T all set-default-catalog;
DEFAULT_CATALOGS_SCRIPT+=$(SPRINGER) list catalog


LIST_SCRIPT =$(SPRINGER) list catalogs;
LIST_SCRIPT+=$(SPRINGER) list packages;
LIST_SCRIPT+=$(SPRINGER) list books;
LIST_SCRIPT+=$(SPRINGER) list catalog -l

DOWNLOAD_SCRIPT =$(SPRINGER) -L de -T med download --dest-path de/nursing;
DOWNLOAD_SCRIPT+=$(SPRINGER) download -p computer -d computer --format epub

SVGS= $(TARGETS:=.svg)

.PHONY: $(SVGS)

all: $(SVGS)

default_catalogs_demo.svg:
	@$(call PLAY,$(DEFAULT_CATALOGS_SCRIPT)) | $(call RECORD,$@,30)

list_demo.svg:
	@$(call PLAY,$(LIST_SCRIPT)) | $(call RECORD,$@,30)

downloading_demo.svg:
	@$(call PLAY,$(DOWNLOAD_SCRIPT)) | $(call RECORD,$@,15)

clean:
	@/bin/rm -rf computer de en *.pdf *.epub DOWNLOAD_ERRORS.txt

immaculate: clean
	@/bin/rm -f *.svg

# SNAIL: function snail() { awk -v s="${1:-'0.3'}" 'system("sleep " s) {exit} 1' }
