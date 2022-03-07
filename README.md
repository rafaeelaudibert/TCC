# Conferences Insight

This is the companion repository to my graduation thesis titled "The Evolution of AI and Machine Learning: The Analysis of Impact, Leadership and Influence over the Last Decades", advised by Prof. Dr. Anderson Rocha Tavares, and co-advised by Prof. Dr. Luís da Cunha Lamb. This work is going to be presented as partial fullfilment for the Bachelor in Computer Science degree at [INF](https://inf.ufrgs.br)-[UFRGS](https://ufrgs.br).

:construction: This is still work in progress, so don't expect everything to be properly documented and usable. When the thesis is complete and published, I'll be linking it here. Also, the final thesis PDF will be added to this repository when possible.

## The dataset

The `dblp` dataset is generated from the XML dump available at [https://dblp.uni-trier.de/xml/dblp.xml.gz](https://dblp.uni-trier.de/xml/dblp.xml.gz). We do need, however, a properly parsed JSON dataset to run our code on.

You can automate this running `./scripts/download_dblp.sh` in a shell.
It will automatically download the required python libraries, DBLP's dataset and converting it to a JSON file located at the root of the project

## DBLP Arnet dataset

We also use the DBLP arnet dataset available [here](https://www.aminer.cn/citation) based on a paper by Tang et al.

## The library

While developing this project, we had to parse a huge XML file into a JSON file (as you can see in the previous section). To achieve so, we had to stream both the XML reading as the JSON writing. Using the already existent [jsonstreams](https://github.com/dcbaker/jsonstreams) and [xmltodict](https://github.com/martinblech/xmltodict) libraries, the [streamxml2json](https://github.com/rafaeelaudibert/streamxml2json) library was built.

It's not extremely overcomplicated, barely scratching the surface of the underlying libraries, but it is extremely simple to use when using it for what it was meant to do: no memory footprint when handling multi-gigabyte files.

## Author

:wizard: [Rafa Audibert](https://www.rafaaudibert.dev)
