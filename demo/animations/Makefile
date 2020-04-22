# demo/Makefile - create GIF animations to demonstrate
#                 how to use the springer texbook download tool
#
#                 *automagically*

SPRINGER= springer

TARGETS = get-default-catalog
TARGETS+= set-default-catalog
TARGETS+= list-catalog
TARGETS+= list-catalog-long
TARGETS+= list-packages
TARGETS+= list-packages-long
TARGETS+= list-books
TARGETS+= list-books-long
TARGETS+= download-catalog
TARGETS+= download-package
TARGETS+= download-books


CASTS= $(TARGETS:=.cast)
GIFS= $(TARGETS:=.gif)

PLAY= ./demo.py "$1"

RFLAGS= -i 0.5 --overwrite -q

RECORD= asciinema rec $1 $(RFLAGS)

SPEEDUP= asciinema rec -c 'asciinema play -i 1 -s $1 $2' $2.fast

CAST2GIF= asciicast2gif
C2GFLAGS= -s 5 -w 100

GET_DEFAULT_CATALOG_SCRIPT=springer get-default-catalog;1;

SET_DEFAULT_CATALOG_SCRIPT+=springer --language de set-default-catalog;1;
SET_DEFAULT_CATALOG_SCRIPT+=springer --language en set-default-catalog;1;
SET_DEFAULT_CATALOG_SCRIPT+=springer --language de --topic med set-default-catalog;1;
SET_DEFAULT_CATALOG_SCRIPT+=springer --language en --topic all set-default-catalog;1;

LIST_CATALOG_SCRIPT=springer list catalog;1;
LIST_CATALOG_LONG_SCRIPT=springer list catalog -l;2;

LIST_PACKAGES_SCRIPT=springer list packages;1;
LIST_PACKAGES_LONG_SCRIPT=springer list packages -l;2;

LIST_BOOKS_SCRIPT=springer list books;2;
LIST_BOOKS_LONG_SCRIPT=springer list books -n 'A Beginners Guide to Python 3 Programming' -l;1;

DOWNLOAD_CATALOG_SCRIPT=springer download catalog;1200;
DOWNLOAD_PACKAGE_SCRIPT=springer download package -n 'Computer Science';300;
DOWNLOAD_BOOKS_SCRIPT=springer download books -n python;240;

LONG_DEMO_SCRIPT= springer get-default-catalog;1;
LONG_DEMO_SCRIPT+= springer list catalog;1;
LONG_DEMO_SCRIPT+= springer list packages;1;
LONG_DEMO_SCRIPT+= springer list packages -n 'Computer Science' -l;2;
LONG_DEMO_SCRIPT+= springer download books -n 'python' -f epub -d epubs ;240;

all: $(GIFS)

get-default-catalog.cast:
	@$(call PLAY,$(GET_DEFAULT_CATALOG_SCRIPT)) | $(call RECORD,$@)

get-default-catalog.gif: get-default-catalog.cast clean_fast
	$(call SPEEDUP,0.5,$<)
	@$(CAST2GIF) $(C2GFLAGS) -h 3 $<.fast $@

set-default-catalog.cast: 
	@springer -L en -T all set-default-catalog > /dev/null
	@$(call PLAY,$(SET_DEFAULT_CATALOG_SCRIPT)) | $(call RECORD,$@)
	@springer -L en -T all set-default-catalog > /dev/null

set-default-catalog.gif: set-default-catalog.cast clean_fast
	$(call SPEEDUP,0.5,$<)
	@springer -L en -T all set-default-catalog
	@$(CAST2GIF) $(C2GFLAGS) -h 13 $<.fast $@

list-catalog.cast:
	@$(call PLAY,$(LIST_CATALOG_SCRIPT)) | $(call RECORD,$@)

list-catalog.gif: list-catalog.cast
	@$(CAST2GIF) $(C2GFLAGS) -h 6 $< $@

list-catalog-long.cast:
	@$(call PLAY,$(LIST_CATALOG_LONG_SCRIPT)) | $(call RECORD,$@)

list-catalog-long.gif: list-catalog-long.cast
	@$(CAST2GIF) $(C2GFLAGS) -h 10 $< $@

list-packages.cast:
	@$(call PLAY,$(LIST_PACKAGES_SCRIPT)) | $(call RECORD,$@)

list-packages.gif: list-packages.cast
	@$(CAST2GIF) $(C2GFLAGS) -h 23 $< $@

list-packages-long.cast:
	@$(call PLAY,$(LIST_PACKAGES_LONG_SCRIPT)) | $(call RECORD,$@)

list-packages-long.gif: list-packages-long.cast
	@$(CAST2GIF) $(C2GFLAGS) -h 10 $< $@

list-books.cast:
	@$(call PLAY,$(LIST_BOOKS_SCRIPT)) | $(call RECORD,$@)

list-books.gif: list-books.cast
	@$(CAST2GIF) $(C2GFLAGS) -h 10 $< $@

list-books-long.cast:
	@$(call PLAY,$(LIST_BOOKS_LONG_SCRIPT)) | $(call RECORD,$@)

list-books-long.gif: list-books-long.cast
	@$(CAST2GIF) $(C2GFLAGS) -h 22 $< $@

download-catalog.cast:
	@$(call PLAY,$(DOWNLOAD_CATALOG_SCRIPT)) | $(call RECORD,$@)

download-catalog.gif: download-catalog.cast clean_fast
	$(call SPEEDUP,10,$<)
	@$(CAST2GIF) $(C2GFLAGS) -h 2 $<.fast $@

download-package.cast:
	@$(call PLAY,$(DOWNLOAD_PACKAGE_SCRIPT)) | $(call RECORD,$@)

download-package.gif: download-package.cast clean_fast
	$(call SPEEDUP,10,$<)
	@$(CAST2GIF) $(C2GFLAGS) -h 2 $<.fast $@

download-books.cast:
	@$(call PLAY,$(DOWNLOAD_BOOKS_SCRIPT)) | $(call RECORD,$@)

download-books.gif: download-books.cast clean_fast
	$(call SPEEDUP,1,$<)
	@$(CAST2GIF) $(C2GFLAGS) -h 2 $<.fast $@

long-demo.cast:
	@$(call PLAY,$(LONG_DEMO_SCRIPT)) | $(call RECORD,$@)

long-demo.gif: long-demo.cast clean_fast
	$(call SPEEDUP,1,$<)
	@$(CAST2GIF) $(C2GFLAGS) -h 10 $<.fast $@

clean_fast:
	@/bin/rm -f *.fast

clean: clean_fast
	@/bin/rm -rf  *.pdf *.epub DOWNLOAD_REPORT.txt Computer_Science epubs

immaculate: clean
	@/bin/rm -f $(CASTS) $(GIFS)

