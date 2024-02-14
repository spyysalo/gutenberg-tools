# gutenberg-tools

Tools for working with Project Gutenberg texts (https://www.gutenberg.org/)

## Quickstart

Download and unpack catalog

```
wget https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv.gz
gunzip pg_catalog.csv.gz
```

Mirror Gutenberg text files

```
rsync -av --del aleph.gutenberg.org::gutenberg-epub aleph.gutenberg.org --include '*.txt' --include '*/' --exclude '*' --prune-empty-dirs
```

Convert to JSONL

```
python3 gutenberg_to_jsonl.py pg_catalog.csv.gz aleph.gutenberg.org > gutenberg.jsonl
```
