# Springer Downloader

Springer Nature is offering free access to a range of essential textbooks:

https://www.springernature.com/gp/librarians/news-events/all-news-articles/industry-news-initiatives/free-access-to-textbooks-for-institutions-affected-by-coronaviru/17855960

This script pulls the Excel catalog of available books as a Pandas DataFrame,
builds a list of URLs for the PDF versions of each title and downloads the
files into a 'books' directory in the current working directory. If a file
with the book's title already exists, the title is not downloaded.

It's a quick and dirty script, but seems to get the job done.
