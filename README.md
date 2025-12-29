# Conferences Insight

This is the companion repository to my graduation thesis titled "The Evolution of AI and Machine Learning: The Analysis of Impact, Leadership and Influence over the Last Decades", advised by Prof. Dr. Anderson Rocha Tavares, and co-advised by Prof. Dr. Luís da Cunha Lamb. This work is going to be presented as partial fullfilment for the Bachelor in Computer Science degree at [INF](https://inf.ufrgs.br)-[UFRGS](https://ufrgs.br).

The final form of the thesis can be found [here](./output/thesis.pdf). You can also find it online on [LUME](https://lume.ufrgs.br/handle/10183/245533). This thesis was also published on [arXiv](https://arxiv.org/abs/2205.13131) and the Journal of Applied Logics Vol. 10 No. 5 2023

Cite as

```bibtex
@misc{audibert2024evolutionaimachinelearning,
      title={On the Evolution of A.I. and Machine Learning: Towards a Meta-level Measuring and Understanding Impact, Influence, and Leadership at Premier A.I. Conferences},
      author={Rafael B. Audibert and Henrique Lemos and Pedro Avelar and Anderson R. Tavares and Luís C. Lamb},
      year={2024},
      eprint={2205.13131},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2205.13131},
}
```

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

## Acknowledgments

See [ACKNOWLEDGMENTS](./ACKNOWLEDGEMENTS)

## License

MIT
