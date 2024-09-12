Ty Friedman - images.py

The images.py program scans websites for images and downloads them to a specified location.

Usage: images.py [-d DESTINATION -n CPUS -f FILETYPES] URL

Crawl the given URL for the specified FILETYPES and download the files to the
DESTINATION folder using CPUS cores in parallel.

    -d DESTINATION      Save the files to this folder (default: .)
    -n CPUS             Number of CPU cores to use (default: 1)
    -f FILETYPES        List of file types: jpg, mp3, pdf, png (default: all)

Multiple FILETYPES can be specified in the following manner:

    -f jpg,png
    -f jpg -f png
