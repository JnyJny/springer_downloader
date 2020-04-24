# `springer`

![Downloading](https://github.com/JnyJny/springer_downloader/raw/master/demo/animations/download-catalog.gif)
__Springer Textbook Bulk Download Tool__

## NOTICE

The author of this software is not affiliated with Springer and this
tool is not authorized or supported by Springer. Thank you to
Springer for making these high quality textbooks available at no
cost.


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

## Overview

This tool automates the process of downloading the Springer-provided
Excel catalogs, locating URLs and downloading the files in PDF or epub
format.

Catalogs are lists of books in a specific _language_, spanning a
_topic_. Catalogs are further subdivided into _packages_ which are
books grouped by sub-topics.

Textbooks can be downloaded by; title, package name or the entire
catalog. Title and package names can be incompletely specified and
are case-insensitive. 

The available languages are: English & German.

The available topics are: _All Disciplines_ and _Emergency Nursing_.

**Note: The _Emergency Nursing_ topic is not available in English.**

## Source and License

Full source is available on
[GitHub](https://github.com/JnyJny/springer_downloader) and it is
licensed under the
[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)
license.

## Installation

This utility can be installed using `pip`:

`$ python3 -m pip install springer`

Or from the latest source on GitHub:

`$ python3 -m pip install git+https://github.com/JnyJny/springer_downloader`

**Usage**:

```console
$ springer [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-L, --language [en|de]`: Choose catalog language
* `-T, --topic [all|med]`: Choose a catalog topic.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `clean-catalog`: Remove cached catalogs.
* `download`: Download textbooks from Springer This command...
* `get-default-catalog`: Print the default catalog identifier.
* `list`: List books, package, packages, catalog or...
* `refresh-catalog`: Refresh the cached catalog of springer...
* `set-default-catalog`: Set default catalog language and topic.

## `springer clean-catalog`

Remove cached catalogs.

__Examples__

Remove the cached default catalog:

`$ springer clean-catalog --force`

Remove the cached German language _Emergency Nursing_ catalog:

`$ springer --language de --topic med clean-catalog --force`

Remove all catalogs:

`$ springer clean-catalog --force --all`

**Usage**:

```console
$ springer clean-catalog [OPTIONS]
```

**Options**:

* `-F, --force`
* `--all`
* `--help`: Show this message and exit.

## `springer download`

Download textbooks from Springer

This command downloads textbooks from Springer to the local host. Files
are saved by default in PDF format to the current working directory.

If a download is interrupted by the user, it can be later restarted where
the interruption occurred without downloading previous files. 

Problems encountered while downloading files are logged to:

`dest-path/DOWNLOAD_REPORT.txt`

__Examples__

Download all books in the default catalog in PDF format to the
current directory:

`$ springer download books`

Download all books in EPUB format whose title includes 'python':

`$ springer download books --name python --file-format epub`

Download all books into directories grouped by package:

`$ springer download packages --dest-path by_pkgs

Download all books in a specific package in EPUB format:

`$ springer download package --name 'Computer Science' --file-format epub`

Download all books in packages whose name includes `Science`:

`$ springer download package --name science --dest sciences`

Download all books in all catalogs [en-all, de-all, de-med] in EPUB format:

`$ springer download catalogs --file-format epub`

The `catalogs` download subcommand will create a set of directories by language
and topic for each catalog and save downloaded files into the appropriate
directory, eg:


- dest-path/English/All_Disciplines/package_name/title.fmt
- dest-path/German/All_Disciplines/package_name/title.fmt
- dest-path/German/Emergency_Nursing/package_name/title.fmt

The `package` and `packages` subcommands will also save downloaded
files into directories with package names rooted in the destination
path:


dest-path/package_name/title.fmt
...



See Also: `set-default-catalog`, `get-default-catalog`, `list`

**Usage**:

```console
$ springer download [OPTIONS] [catalogs|catalog|packages|package|books]
```

**Options**:

* `-n, --name TEXT`: Name to match against title or package.
* `-d, --dest-path PATH`: Destination directory for downloaded files.  [default: /Users/ejo/local/springer]
* `-f, --format [pdf|epub]`: [default: pdf]
* `-W, --over-write`: Over write downloaded files.  [default: False]
* `--help`: Show this message and exit.

## `springer get-default-catalog`

Print the default catalog identifier.

This is the default catalog that will be used when listing books and packages
and the user has not specified a --language or --topic on the command line.

**Usage**:

```console
$ springer get-default-catalog [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `springer list`

List books, package, packages, catalog or catalogs.

Display information about books, packages, and catalogs. Packages
are sets of books grouped by subject.

__Examples__

List titles available in the default catalog:

`$ springer list books`

List packages available in the default catalog:

`$ springer list packages`

List titles available in the German language, all disciplines catalog:

`$ springer --language de --topic all list books`

List all eBook packages in the default catalog:

`$ springer list packages`

List all eBook packages in the default catalog whose name match:

`$ springer list package -m science`

List information about the current catalog:

`$ springer list catalog`

List information about the Germal language, Emergency Nursing catalog:

`$ springer --language de --topic med list catalog`

**Usage**:

```console
$ springer list [OPTIONS] [catalogs|catalog|packages|package|books]
```

**Options**:

* `-n, --name TEXT`: Name to match against title or pacakge.
* `-l, --long-format`: Display selected information in a longer format.  [default: False]
* `--help`: Show this message and exit.

## `springer refresh-catalog`

Refresh the cached catalog of springer textbooks.

If `--all` is specified, the `--url` option is ignored.

__Examples__

Update English language catalog:

`$ springer --language en refresh`

Update German language catalog whose topic is 'all':

`$ springer --language de --topic all refresh`

Update German language catalog whose topic is 'med' with a new url:

`$ springer -l de -d med refresh --url https://example.com/api/endpoint/something/v11`

__NOTE: THIS URL DOES NOT REPLACE THE DEFAULT URL FOR THE TARGET CATALOG__

Update all catalogs:

`$ springer refresh-catalog --all`

**Usage**:

```console
$ springer refresh-catalog [OPTIONS]
```

**Options**:

* `-u, --url TEXT`: URL for Excel-formatted catalog.
* `--all`
* `--help`: Show this message and exit.

## `springer set-default-catalog`

Set default catalog language and topic.

__Examples__

Set the default catalog to German language:

`$ springer --language de set-default-catalog`

Set the default catalog to German and emergency nursing:

`$ springer --language de --topic med set-default-catalog`

Set the default catalog to English and all disciplines topic:

`$ springer --language en --topic all set-default-catalog`

Note: The only English language catalog is `en-all`.

**Usage**:

```console
$ springer set-default-catalog [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
