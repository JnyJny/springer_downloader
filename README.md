# `springer`

Springer Textbook Bulk Download Tool

**NOTICE**:

Author not affiliated with Springer and this tool is not authorized
or supported by Springer. Thank you to Springer for making these
high quality textbooks available at no cost. 


>"With the Coronavirus outbreak having an unprecedented impact on
>education, Springer Nature is launching a global program to support
>learning and teaching at higher education institutions
>worldwide. Remote access to educational resources has become
>essential. We want to support lecturers, teachers and students
>during this challenging period and hope that this initiative will go
>some way to help.
>
>Institutions will be able to access more than 500 key textbooks
>across Springer Nature’s eBook subject collections for free. In
>addition, we are making a number of German-language Springer medical
>training books on emergency nursing freely accessible.  These books
>will be available via SpringerLink until at least the end of July."

[Source](https://www.springernature.com/gp/librarians/news-events/all-news-articles/industry-news-initiatives/free-access-to-textbooks-for-institutions-affected-by-coronaviru/17855960)

This tool automates the tasks of downloading the Excel-formatted
catalogs and downloading the files described in the catalog.

This utility can be installed using `pip`:

`$ python3 -m pip install springer`

Or the latest from master:

`$ python3 -m pip install git+https://github.com/JnyJny/springer_downloader`

The source is available on [GitHub](https://github.com/JnyJny/springer_downloader).

**Usage**:

```console
$ springer [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-L, --lang [en|de]`: Choose catalog language  [default: en]
* `-D, --description [all|med]`: Choose a catalog description.  [default: all]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `clean`: Removes the cached catalog.
* `download`: Download textbooks from Springer.
* `list`: List books, package, packages, catalog or...
* `refresh`: Refresh the cached catalog of Springer...

## `springer clean`

Removes the cached catalog.

Examples

Remove the English language, all disciplines cached catalog:

`$ springer clean --force`

Remove the German language emergency nursing cached catalog:

`$ springer -L de -D med clean --force`

Remove all catalogs:

`$ springer clean --force --all`

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

If the --all option is specified, the --dest-path option specifies the
root directory where files will be stored. Each catalog will save 
it's textbooks to:

dest_path/language/description/book_file_name.fmt

Files that fail to download will be logged to a file named:

dest_path/DOWNLOAD_ERRORS.txt

The log entries will have the date and time of the attempt,
the HTTP status code and the URL that was attempted.


EXAMPLES

Download all books in PDF format to the current directory:

`$ springer download`

Download all books in EPUB format to the current directory:

`$ springer download --format epub`

Download all books in PDF format to a directory `pdfs`:

`$ springer download --dest-path pdfs`

Download books in PDF format to `pdfs` with overwriting:

`$ springer download --dest-path pdfs --over-write`

Download all books in PDF from the German/All_Disciplines catalog:

`$ springer -L de -D all download --dest-path german/all/pdfs`

Download all books from all catelogs in epub format:

`$ springer download --all --format epub`

Download all books in the 'Computer Science' package in pdf format:

`$ springer download -p Computer`

**Usage**:

```console
$ springer download [OPTIONS]
```

**Options**:

* `-p, --package-name TEXT`: Package name to match (partial name OK).
* `-f, --format [pdf|epub]`: [default: pdf]
* `-d, --dest-path PATH`: Destination directory for downloaded files.  [default: /Users/ejo/local/springer]
* `-W, --over-write`: Over write downloaded files.  [default: False]
* `--all`: Downloads books from all catalogs.
* `--help`: Show this message and exit.

## `springer list`

List books, package, packages, catalog or catalogs,

Examples

List titles available in the default catalog:

`$ springer list books`

List packages available in the default catalog:

`$ springer list packages`

List titles available in the German language, all disciplines catalog:

`$ springer --language de --description all list books`

List all eBook packages in the default catalog:

`$ springer list packages`

List all eBook packages in the default catalog whose name match:

`$ springer list package -m science`

List information about the current catalog:

`$ springer list catalog`

List information about the Germal language, Emergency Nursing catalog:

`$ springer --language de --description med list catalog`

**Usage**:

```console
$ springer list [OPTIONS] [catalogs|catalog|packages|package|books]
```

**Options**:

* `-m, --match TEXT`: String used for matching.
* `-l, --long-format`: Display selected information in a longer format.  [default: False]
* `--help`: Show this message and exit.

## `springer refresh`

Refresh the cached catalog of Springer textbooks.

If --all is specified, the --url option is ignored.

Examples

Update English language catalog:

`$ springer --language en refresh`

Update German language catalog whose description is 'all':

`$ springer --language de --description all refresh`

Update German language catalog whose description is 'med' with a new URL:

`$ springer -L de -D med refresh --url https://example.com/api/endpoint/something/v11`

Update all catalogs:

`$ springer refresh --all`

**Usage**:

```console
$ springer refresh [OPTIONS]
```

**Options**:

* `-u, --url TEXT`: URL for Excel-formatted catalog
* `--all`
* `--help`: Show this message and exit.
