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
LIST_BOOKS_LONG_SCRIPT=springer list books -l;3;

DOWNLOAD_CATALOG_SCRIPT=springer download catalog;1200;
DOWNLOAD_PACKAGE_SCRIPT=springer download package -n 'Computer Science';300;
DOWNLOAD_BOOKS_SCRIPT=springer download books -n python;240;

all: $(GIFS)

get-default-catalog.cast:
	@$(call PLAY,$(GET_DEFAULT_CATALOG_SCRIPT)) | $(call RECORD,$@)

get-default-catalog.gif: get-default-catalog.cast
	@$(CAST2GIF) $(C2GFLAGS) -h 5 $< $@

set-default-catalog.cast: 
	@springer -L en -T all set-default-catalog > /dev/null
	@$(call PLAY,$(SET_DEFAULT_CATALOG_SCRIPT)) | $(call RECORD,$@)
	@springer -L en -T all set-default-catalog > /dev/null

set-default-catalog.gif: set-default-catalog.cast
	@springer -L en -T all set-default-catalog
	@$(CAST2GIF) $(C2GFLAGS) -h 13 $< $@

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
	@$(CAST2GIF) $(C2GFLAGS) -h 24 $< $@

list-packages-long.cast:
	@$(call PLAY,$(LIST_PACKAGES_LONG_SCRIPT)) | $(call RECORD,$@)

list-packages-long.gif: list-packages-long.cast
	@$(CAST2GIF) $(C2GFLAGS) -h 24 $< $@

list-books.cast:
	@$(call PLAY,$(LIST_BOOKS_SCRIPT)) | $(call RECORD,$@)

list-books.gif: list-books.cast
	@$(CAST2GIF) $(C2GFLAGS) -h 24 $< $@

list-books-long.cast:
	@$(call PLAY,$(LIST_BOOKS_LONG_SCRIPT)) | $(call RECORD,$@)

list-books-long.gif: list-books-long.cast
	@$(CAST2GIF) $(C2GFLAGS) -h 24 $< $@

download-catalog.cast:
	@$(call PLAY,$(DOWNLOAD_CATALOG_SCRIPT)) | $(call RECORD,$@)

download-catalog.gif: download-catalog.cast
	@rm -f $<.fast
	$(call SPEEDUP,20,$<)
	@$(CAST2GIF) $(C2GFLAGS) -h 4 $<.fast $@

download-package.cast:
	@$(call PLAY,$(DOWNLOAD_PACKAGE_SCRIPT)) | $(call RECORD,$@)

download-package.gif: download-package.cast
	@rm -f $<.fast
	$(call SPEEDUP,10,$<)
	@$(CAST2GIF) $(C2GFLAGS) -h 4 $<.fast $@

download-books.cast:
	@$(call PLAY,$(DOWNLOAD_BOOKS_SCRIPT)) | $(call RECORD,$@)

download-books.gif: download-books.cast
	@rm -f $<.fast
	$(call SPEEDUP,10,$<)
	@$(CAST2GIF) $(C2GFLAGS) -h 4 $<.fast $@



clean:
	@/bin/rm -f  *.pdf *.epub DOWNLOAD_REPORT.txt $(CASTS)

immaculate: clean
	@/bin/rm -f $(GIFS)

# SNAIL: function snail() { awk -v s="${1:-'0.3'}" 'system("sleep " s) {exit} 1' }
