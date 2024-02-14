#!/usr/bin/env python3

# Convert Project Gutenberg texts to JSONL format.

# Call with catalog file and base directory for Gutenberg mirror.
# You can get these e.g. as follows:
#
# Catalog:
#
#     wget https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv.gz
#     gunzip pg_catalog.csv.gz
#
# Mirror:
#
#     rsync -av --del aleph.gutenberg.org::gutenberg-epub aleph.gutenberg.org --include '*.txt' --include '*/' --exclude '*' --prune-empty-dirs
#
# And then call this script with
#
#     python3 gutenberg_to_jsonl.py pg_catalog.csv.gz aleph.gutenberg.org

import sys
import os
import re
import csv
import json

from logging import warning, error
from argparse import ArgumentParser


START_RE = re.compile(r'START OF (THE|THIS) PROJECT GUTENBERG EBOOK')

END_RE = re.compile(r'END OF THE PROJECT GUTENBERG EBOOK')


def argparser():
    ap = ArgumentParser()
    ap.add_argument('catalog')
    ap.add_argument('basedir')
    return ap


def is_start_line(line):
    # Some variation of "*** START OF THE PROJECT GUTENBERG EBOOK ..."
    return '***' in line and START_RE.search(line) is not None


def is_end_line(line):
    # Some variation of "*** END OF THE PROJECT GUTENBERG EBOOK ..."
    return '***' in line and END_RE.search(line) is not None


def convert(item, args):
    n = item['Text#']

    dn = os.path.join(args.basedir, n)
    if not os.path.isdir(dn):
        raise Exception(f'missing directory {dn}')

    fn = os.path.join(dn, f'pg{n}.txt')
    if not os.path.isfile(fn):
        raise Exception(f'missing file {fn}')

    with open(fn) as f:
        text = f.read()

    lines = text.splitlines()

    start_indices = [i for i in range(len(lines)) if is_start_line(lines[i])]
    end_indices = [i for i in range(len(lines)) if is_end_line(lines[i])]

    if not start_indices:
        raise Exception(f'missing start in {fn}')
    elif len(start_indices) > 1:
        warning(f'multiple starts in {fn}: {start_indices}')

    if not end_indices:
        raise Exception(f'missing end in {fn}')
    elif len(end_indices) > 1:
        warning(f'multiple ends in {fn}: {end_indices}')

    start_idx = start_indices[-1]
    end_idx = end_indices[0]

    text_lines = lines[start_idx+1:end_idx]
    text = '\n'.join(text_lines).strip()

    return text


def main(argv):
    args = argparser().parse_args(argv[1:])

    with open(args.catalog) as f:
        catalog = list(csv.DictReader(f))

    errors = 0
    for i in catalog:
        if i['Type'] != 'Text':
            continue
        n = i['Text#']

        try:
            text = convert(i, args)
            data = {
                'id': f'gutenberg:{n}',
                'text': text,
                'meta': i
            }
            print(json.dumps(data, ensure_ascii=False))
        except Exception as e:
            error(f'processing {n}: {e}')
            errors += 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
