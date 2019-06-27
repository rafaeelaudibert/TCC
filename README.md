# DBLP dataset

With the `dblp` dataset, extract it and fetch the articles information to a `json` file

## Steps

Make sure you already have `gzip` and `wget` installed (comes in most of Linux distros)

```
$ wget https://dblp.uni-trier.de/xml/dblp.xml.gz
$ gunzip dblp.xml.gz
$ python3 xmltodict.py 2 < dblp.xml > dblp.marshal
$ python3 marshal2json.py
```