import json
from tqdm import tqdm

DATASET_SIZE = 4_107_340
GML_BASE_PATH = '../GML/'
DBLP_FILENAME = 'dblp_papers_v11.txt'
CONFERENCES = ['1184914352', '1127325140', '1203999783', '1158167855',
               '1124077590', '1164975091', '1180662882', '1130985203',
               '1188739475', '1192655580', '1173951661', '1140684652',
               '1135342153']
CONFERENCES_MAP = {key: val for key, val in zip(CONFERENCES, [
                                                'AAAI', 'NIPS', 'IJCAI', 'CVPR', 'ECCV', 'ICCV', 'ICML', 'KDD', 'ACL', 'EMNLP', 'NAACL', 'SIGIR', 'WWW'])}  # nopep8

THE_CONFERENCE = '1158167855'  # CVPR
CONFERENCE_NAME = 'CVPR'


def get_data(dictionary: dict = {}) -> dict:
    '''Given a dictionary, parse the necessary data contained in it'''
    return {
        'id': dictionary.get('id', 0),
        'title': dictionary.get('title', ''),
        'year': int(dictionary.get('year', 0)),
        'authors': dictionary.get('authors', []),
        'venue_id': dictionary.get('venue', {}).get('id', None),
        'references': dictionary.get('references', [])
    }


json_filename = './dblp_arnet/CS_Rankings.json'
with open(json_filename, 'r') as f:
    conference_papers = json.load(f)


# Store older_papers in an arrray
older_papers = {}
# Dict with data
citation_data = {}

# Iterate through all the dataset years
for year in tqdm(range(1890, 2020)):

    # Add papers and authors to be referenced later
    for paper in conference_papers.get(str(year), []):
        older_papers[paper['id']] = paper
    citation_data[year] = {}

    # Iterate over the papers adding them to the G graph
    for paper in tqdm(conference_papers.get(str(year), [])):
        if paper['venue_id'] == THE_CONFERENCE:
            for citation_id in paper['references']:
                if citation_id in older_papers.keys():
                    citation_data[year][CONFERENCES_MAP[older_papers[citation_id]['venue_id']]] = citation_data[year].get(CONFERENCES_MAP[older_papers[citation_id]['venue_id']], 0) + 1  # nopep8
                else:
                    citation_data[year]['OTHER'] = citation_data[year].get(
                        'OTHER', 0) + 1

csv_array = []
for year in citation_data:
    for conference in citation_data[year]:
        csv_array.append((year, conference, citation_data[year][conference]))

output_filename = f'./CSV/{CONFERENCE_NAME}.csv'
with open(output_filename) as f:
    f.write("year, conference, value\n")

    for thing in csv_array:
        f.write(','.join(map(str, thing)) + '\n')
