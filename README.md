# `springer`

Springer Textbook Bulk Download Tool

NOTICE:

Author not affiliated with Springer and this tool is not authorized
or supported by Springer. Thank you to Springer for making these
high quality textbooks available at no cost. 

**Usage**:

```console
$ springer [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-L, --lang [en|de]`: Choose catalog language  [default: en]
* `-C, --category [all|med]`: Choose a catalog catagory.  [default: all]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `catalogs`: List available catalogs.
* `clean`: Removes the cached catalog.
* `download`: Download textbooks from Springer.
* `list`: List textbooks in the catalog.
* `refresh`: Refresh the cached catalog of Springer...

## `springer catalogs`

List available catalogs.
    

**Usage**:

```console
$ springer catalogs [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `springer clean`

Removes the cached catalog.
    

**Usage**:

```console
$ springer clean [OPTIONS]
```

**Options**:

* `-F, --force`
* `--all`
* `--help`: Show this message and exit.

## `springer download`

Download textbooks from Springer.

This command will download all the textbooks found in the catalog
of free textbooks provided by Springer. The default file format 
is PDF and the files are saved by default to the current working
directory.

If a download is interrupted, you can re-start the download and it
will skip over files that have been previously downloaded and pick up
where it left off. 

If the --all option is specified, the --dest=path option specifies the
root directory where files will be stored. Each catalog will save 
it's textbooks to:

dest_path/language/category/book_file_name.fmt


EXAMPLES

Download all books in PDF format to the current directory:

$ springer download

Download all books in EPUB format to the current directory:

$ springer download --format epub

Download all books in PDF format to a directory `pdfs`:

$ springer download --dest-path pdfs

Download books in PDF format to `pdfs` with overwriting:

$ springer download --dest-path pdfs --over-write

Download all books in PDF from the German all disciplines catalog:

$ springer -L de -C all download --dest-path german/all/pdfs

Download all books from all catelogs in epub format:

$ springer download --all --dest-path books --format epub

**Usage**:

```console
$ springer download [OPTIONS]
```

**Options**:

* `-d, --dest-path PATH`: Destination directory for downloaded files.  [default: /Users/ejo/local/springer]
* `-f, --format [pdf|epub]`: [default: pdf]
* `-W, --over-write`: Over write downloaded files.  [default: False]
* `--all`: Downloads books from all catalogs.
* `--help`: Show this message and exit.

## `springer list`

List textbooks in the catalog.
    

**Usage**:

```console
$ springer list [OPTIONS]
```

**Options**:

* `-f, --format [pdf|epub]`: [default: pdf]
* `-p, --show-path`: Show generated filename for each book.
* `--help`: Show this message and exit.

## `springer refresh`

Refresh the cached catalog of Springer textbooks.

If --all is specified, the --url option is ignored.

Examples

Update English language catalog:

$ springer --language en refresh

Update German language catalog whose category is 'all':

$ springer --language de --category all refresh

Update German language catalog whose category is 'med' with a new URL:

$ springer -L de -C med refresh --url https://example.com/api/endpoint/something/v11

Update all catalogs:

$ springer refresh --all

**Usage**:

```console
$ springer refresh [OPTIONS]
```

**Options**:

* `-u, --url TEXT`: URL for Excel-formatted catalog
* `--all`
* `--help`: Show this message and exit.
