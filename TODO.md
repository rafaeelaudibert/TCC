## Graphs to be generated

- Authors and Papers (Authors with edges to authored paper, and papers with edges to cited papers) -> `AP`
- Citation Graph (Papers to cited papers) -> `CI`
- Collaboration Graph (Authors to authors which authored some paper together) -> `CO`
- Author Citation Graph (Authors with edges to cited authors) -> `AC`

## Tasks to do centralities

| Type of features    | Description                                   | Done IA        | Done All |
| ------------------- | --------------------------------------------- | -------------- | -------- | --------- |
| Graph Generation    | Generate the graphs we want to do             | AP, CI, CO, AC |          | :loading: |
| Centralities        | Degree, Betweenness, Closeness, PR, etc       | AP, CI, CO, AC |          | :loading: |
| Most central        | For each centrality, try explain most central |                |          | :loading: |
| Community detection | Self-explainable                              |                |          |

## TODO LIST

| What                                                                                                                                                                                                                                                                             | Completed in |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| Update script to download data                                                                                                                                                                                                                                                   | 02/13/2021   |
| streamxml2json library                                                                                                                                                                                                                                                           | 02/13/2021   |
| Regenerate data until 2021                                                                                                                                                                                                                                                       | IN PROGRESS  |
| Finish infering countries (and the do countries centrality and possibly affiliation centrality. After, China/EUA/Russia Cooperation, and then Brain "Piracy" - Find people moving from one country to the other)                                                                 |              |
| Community inference/cycle detection (A cites B cites C cites A ...) Community detection needs a lot of RAM, so we need to see if we are really going to be able to do it. Maybe try with a different library than networkX, and a different UI tool than the one we tried to use |              |
| Small dashboard to check how many papers there are for each conference in the last N years (auto-updating)                                                                                                                                                                       |              |
| Self-citing                                                                                                                                                                                                                                                                      |              |
| Most co-authors, and average co-authors per paper per area                                                                                                                                                                                                                       |              |
