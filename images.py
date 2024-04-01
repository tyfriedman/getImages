#!/usr/bin/env python3

''' images.py - Web crawler to download files in parallel. '''

from typing import Iterator, Optional

import os
import concurrent.futures
import itertools
import re
import sys
import tempfile
import time
import urllib.parse
import pprint

from urllib.parse import urljoin

import requests

# Constants
FILE_REGEX = {
    'jpg': [r'<img.*src="?([^\" ]+.jpg)', r'<a.*href="?([^\" ]+.jpg)'],
    'mp3': [r'<audio.*src="?([^\" ]+.mp3)', r'<a.*href="?([^\" ]+.mp3)'],
    'pdf': [r'<a.*href="?([^\" ]+.pdf)'],
    'png': [r'<img.*src="?([^\" ]+.png)', r'<a.*href="?([^\" ]+.png)'],
}

MEGABYTES   = 1<<20
DESTINATION = '.'
CPUS        = 1

# Functions

def usage(exit_status: int=0) -> None:
    ''' Print usgae message and exit. '''
    print(f'''Usage: images.py [-d DESTINATION -n CPUS -f FILETYPES] URL

Crawl the given URL for the specified FILETYPES and download the files to the
DESTINATION folder using CPUS cores in parallel.

    -d DESTINATION      Save the files to this folder (default: {DESTINATION})
    -n CPUS             Number of CPU cores to use (default: {CPUS})
    -f FILETYPES        List of file types: jpg, mp3, pdf, png (default: all)

Multiple FILETYPES can be specified in the following manner:

    -f jpg,png
    -f jpg -f png''', file=sys.stderr)
    sys.exit(exit_status)

def resolve_url(base: str, url: str) -> str:
    if '://' in url:
        return url
    else:
        url = urljoin(base, url, allow_fragments=True)
        return url

def extract_urls(url: str, file_types: list[str]) -> Iterator[str]:
    response = requests.get(url)
    response.raise_for_status()
    info = response.text
    for key in file_types:
        for rex in FILE_REGEX[key]:
            regex = re.compile(rex)
            for arg in re.findall(regex, info):
                yield resolve_url(url, arg)



def download_url(url: str, destination: str=DESTINATION) -> Optional[str]:
    os.makedirs(destination, exist_ok=True)
    print(f'Downloading {url}...')
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None
    
    path = os.path.join(destination, os.path.basename(url))

    with open(path, 'wb') as file:
        file.write(response.content)
    file.close()
    return path

def crawl(url: str, file_types: list[str], destination: str=DESTINATION, cpus: int=CPUS) -> None:
    start_time = time.time()
    with concurrent.futures.ProcessPoolExecutor(cpus) as executor:
        urls = extract_urls(url, file_types)
        dsts = itertools.repeat(destination)
        files = executor.map(download_url, urls, dsts)

    num_files = 0
    size = 0.0
    for file in files:
        if file:
            num_files += 1
            size += os.stat(str(file)).st_size / (1024 * 1024)

    print(f'Files Downloaded: {num_files}')
    print(f'Bytes Downloaded: {size:0.2f} MB')

    end_time = time.time()
    total_time = end_time - start_time
    bandwidth = size/total_time
    print(f'Elapsed Time:     {total_time:0.2f} s')
    print(f'Bandwidth:        {bandwidth:0.2f} MB/s')


# Main Execution

def main(arguments=sys.argv[1:]) -> None:
    file_types = []
    check = 1
    cpus = 1
    while arguments:
        arg = arguments.pop(0)
        if arg == '-d':
            destination = arguments.pop(0)
        elif arg == '-n':
            cpus = int(arguments.pop(0))
        elif arg == '-f':
            for file_type in arguments.pop(0).split(","):
                file_types.append(file_type)
        elif arg == '-h':
            usage(0)
        elif '-' in arg:
            usage(1)
        else:
            url = arg
            check = 0
        

    if check:
       usage(1)

    if not file_types:
        file_types = ['jpg', 'mp3', 'pdf', 'png']

    crawl(url, file_types, destination, cpus)

if __name__ == '__main__':
    main()
