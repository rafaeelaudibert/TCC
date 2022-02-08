## Graphs to be generated

- Authors and Papers (Authors with edges to authored paper, and papers with edges to cited papers) -> `AP`
- Citation Graph (Papers to cited papers) -> `CI`
- Collaboration Graph (Authors to authors which authored some paper together) -> `CO`
- Author Citation Graph (Authors with edges to cited authors) -> `AC`   

## Tasks to do centralities

| Type of features 	        | Description 	                                        | Done IA           | Done All          |
|---------------	          |-------------	                                        |------------------ |------------------ |
| Graph Generation          | Generate the graphs we want to do                     | AP, CI, CO, AC    |         	        | :loading:
| Centralities     	        | Degree, Betweenness, Closeness, PR, etc               | AP, CI, CO, AC    |         	        | :loading:
| Most central     	        | For each centrality, try explain most central         |         	        |         	        | :loading:
| Community detection       | Self-explainable                                      |         	        |          	        |

## Tasks to do with citations
| Type of features 	        | Description 	                                        | Done IA           | Done All          |
|---------------	          |-------------	                                        |------------------ |------------------ |
| Self-citing               | Detect the areas which most/least self-cite           |         	        |          	        | :loading:
| Cooperation inter-area    | Find what areas tend to cite other areas the most     |         	        |          	        |

## Tasks to do with country and affiliation inference
| Type of features 	               | Description 	                                         | Done IA           | Done All          |
|---------------	                 |-------------	                                         |------------------ |------------------ |
| Countries centrality             | Try to infer country and compute centrality           |         	         |          	       |
| Affiliation centrality           | Try to infer afilliation and compute centrality       |                   |                   |
| China/EUA/Russia Cooperation     | Find out if those countries work together + evolution |         	         |          	       |
| Brain "Piracy"                   | Find people moving from one country to the other      |                   |


> NOTES: Regenerate data until 2021
>        Community detection needs a lot of RAM, so we need to see if we are really going to be able to do it. Maybe try with a different library than networkX, and a different UI tool than the one we tried to use
>        Countries detection is pretty interesting, but might have a lot of papers that we can't detect the country (author affiliation, then matching university -> country)
>        "Little pan" (A cites B cites C cites A ...) - community inference or cycle detection
>        Small dashboard to check how many papers there are for each conference in the last N years (auto-updating)
>        Results
>            Database
>            Data analysis
>                Centralities
>                   Figure 1
>                   Figure 2
>                   Figure 3
>                Communities
>                   Figure 1
>                   Figure 2
>                  
