import sys, marshal
import json
import fire
import re
import pprint
from tqdm import tqdm

PATH_TO_XML = "./dblp.xml"
PATH_TO_MARSHAL = "./dblp.marshal"
DBLP_SIZE = 13_871_537
CATEGORIES = set(
	["article", "inproceedings", "proceedings", "book", "incollection", "phdthesis", "mastersthesis", "www"]
)
DATA_ITEMS = ["title", "booktitle", "journal", "volume", "year", "ee"]
TDATA_ITEMS = ["key", "tag", "title", "booktitle", "journal", "volume", "year", "ee"]
JDATA_ITEMS = ["key", "title", "journal", "volume", "year", "ee"]
CDATA_ITEMS = ["key", "title", "booktitle", "year", "ee"]

# Return the authors
def get_authors(value):
    return value['author'] if type(value['author']) is str else ', '.join(author if type(author) is str else author['#text'] for author in value['author'])

def main(min_year=float("-inf"), max_year=float("inf"), output_filename="dblp.json", conference_name=None, author_name=None):
    output = []
    pbar_out = tqdm(unit=' entries', unit_scale=True, total=DBLP_SIZE)
    pbar_in = tqdm(unit=' articles', unit_scale=True)
    count = 0

    if conference_name is not None:
        conference_regex = re.compile(conference_name)

    if author_name is not None:
        author_regex = re.compile(author_name)
    
    try:
        with open(PATH_TO_MARSHAL, 'rb') as f:
            while True:
                try:
                    info, value = marshal.load(f)

                    if info[1][0] == 'inproceedings' and \
                        float(value['year']) >= min_year and \
                        float(value['year']) <= max_year and \
                        (conference_name is None or conference_regex.match(value['booktitle'])) and \
                        (author_name is None or author_regex.match(get_authors(value))):

                        output.append(value)
                        pbar_in.update(1)
                except KeyError as e:
                    print("KeyError", value, info)
                except EOFError as e:
                    break
                pbar_out.update(1)
                count += 1
    finally:
        pbar_out.close()
        pbar_in.close()

    with open(output_filename, 'w') as f:
        json.dump(output, f, indent=2)

    print("Final count", count)

# Calling main with fire
if __name__ == "__main__":
    fire.Fire(main)
