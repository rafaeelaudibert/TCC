## Graphs to be generated

- Authors and Papers (Authors with edges to authored paper, and papers with edges to cited papers) -> `AP`
- Citation Graph (Papers to cited papers) -> `CI`
- Collaboration Graph (Authors to authors which authored some paper together) -> `CO`
- Author Citation Graph (Authors with edges to cited authors) -> `AC`   

## Tasks to do centralities

| Type of features 	        | Description 	                                        | Done IA           | Done All          |
|---------------	        |-------------	                                        |------------------ |------------------ |
| Graph Generation          | Generate the graphs we want to do                     | AP, CI, CO, AC    |         	        |
| Centralities     	        | Degree, Betweenness, Closeness, PR, etc               | AP, CI, CO, AC    |         	        |
| Most central     	        | For each centrality, try explain most central         |         	        |         	        |
| Community detection       | Self-explainable                                      |         	        |          	        |

## Tasks to do with citations
| Self-citing               | Detect the areas which most/least self-cite           |         	        |          	        |
| Cooperation inter-area    | Find what areas tend to cite other areas the most     |         	        |          	        |

## Tasks to do with country and affiliation inference
| Countries centrality      | Try to infer country and compute centrality           |         	        |          	        |
| Affiliation centrality    | Try to infer afilliation and compute centrality       |                   |                   |
| China/EUA Cooperation     | Find out if those countries work together + evolution |         	        |          	        |


