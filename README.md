# `springer`

Springer Textbook Bulk Download Tool
    

**Usage**:

```console
$ springer [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-n, --dryrun`: List titles and filenames but do not download any textbooks.  [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `download`

## `springer download`

    

**Usage**:

```console
$ springer download [OPTIONS]
```

**Options**:

* `-d, --dest-path PATH`: Destination directory for downloaded files.  [default: /Users/ejo/springer]
* `-u, --url TEXT`: URL for Excel formatted catalog
* `-R, --refresh`: Refresh the cached Springer catalog
* `-f, --format [pdf|epub]`: [default: pdf]
* `-W, --over-write`: Over write downloaded files.  [default: False]
* `--help`: Show this message and exit.
