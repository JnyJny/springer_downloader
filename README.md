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

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `clean`: Removes the cached catalog.
* `download`: Download textbooks from Springer.
* `list`: List textbooks in the catalog.
* `refresh`: Refresh the cached catalog of Springer...
* `urls`: List catalog and content URLS.

## `springer clean`

Removes the cached catalog.
    

**Usage**:

```console
$ springer clean [OPTIONS]
```

**Options**:

* `-F, --force`
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

EXAMPLES

Download all books in PDF format to the current directory.

$ springer download

Download all books in EPUB format to the current directory.

$ springer download --format epub

Download all books in PDF format to a directory `pdfs`.

$ springer download --dest-path pdfs

Download books in PDF format to `pdfs` with overwriting.

$ springer download --dest-path pdfs --over-write

**Usage**:

```console
$ springer download [OPTIONS]
```

**Options**:

* `-d, --dest-path PATH`: Destination directory for downloaded files.  [default: /Users/ejo/local/springer]
* `-f, --format [pdf|epub]`: [default: pdf]
* `-W, --over-write`: Over write downloaded files.  [default: False]
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
    

**Usage**:

```console
$ springer refresh [OPTIONS]
```

**Options**:

* `-u, --url TEXT`: URL for Excel-formatted catalog
* `--help`: Show this message and exit.

## `springer urls`

List catalog and content URLS.
    

**Usage**:

```console
$ springer urls [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
