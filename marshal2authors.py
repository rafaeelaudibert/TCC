import sys, marshal
import json
import fire
import re
import pprint
from tqdm import tqdm

PATH_TO_XML = "./dblp.xml"
PATH_TO_MARSHAL = "./dblp.marshal"
DBLP_SIZE = 6_963_277
CATEGORIES = set(
	["article", "inproceedings", "proceedings", "book", "incollection", "phdthesis", "mastersthesis", "www"]
)
DATA_ITEMS = ["title", "booktitle", "journal", "volume", "year", "ee"]
TDATA_ITEMS = ["key", "tag", "title", "booktitle", "journal", "volume", "year", "ee"]
JDATA_ITEMS = ["key", "title", "journal", "volume", "year", "ee"]
CDATA_ITEMS = ["key", "title", "booktitle", "year", "ee"]

AUTHORS_FOLDER = './turing_awards/'
AUTHORS = [
    "Yoshua Bengio", "Geoffrey E. Hinton", "Yann LeCun",
    "John L. Hennessy", "David A. Patterson", "Tim Berners-Lee",
    "Whitfield Diffie", "Martin E. Hellman", "Michael Stonebraker",
    "Leslie Lamport", "Shafi Goldwasser", "Silvio Micali",
    "Judea Pearl", "Leslie G. Valiant", "Charles P. Thacker",
    "Barbara Liskov", "Edmund M. Clarke", "E. Allen Emerson",
    "Joseph Sifakis", "Frances E. Allen", "Peter Naur",
    "Vinton G. Cerf", "Robert E. Kahn", "Alan C. Kay",
    "Leonard M. Adleman", "Ronald L. Rivest", "Adi Shamir",
    "Ole-Johan Dahl", "Kristen Nygaard", "Andrew Chi-Chih Yao",
    "Jim Gray", "Douglas C. Engelbart", "Amir Pnueli",
    "Manuel Blum", "Edward A. Feigenbaum", "Dabbala Rajagopal Reddy",
    "Juris Hartmanis", "Richard Edwin Stearns", "Butler W. Lampson",
    "Robin Milner", "Fernando J. Corbat", "William Kahan",
    "Ivan E. Sutherland", "John Cocke", "John E. Hopcroft",
    "Robert E. Tarjan", "Richard M. Karp", "Niklaus Wirth",
    "Dennis Ritchie", "Stephen A. Cook", "E. F. Codd",
    "Tony Hoare", "Kenneth E. Iverson", "Robert W. Floyd",
    "John W. Backus", "Michael O. Rabin", "Dana S. Scott",
    "Allen Newell", "Herbert A. Simon", "Donald E. Knuth",
    "Charles W. Bachman", "Edsger W. Dijkstra", "John McCarthy",
    "James Hardy", "Marvin Minsky", "Richard Wesley Hamming",
    "Maurice V. Wilkes", "Alan J. Perlis"
]

# Return the authors
def get_authors(value):

    # Only one author case
    if type(value['author']) is str:
        return value['author']

    # List case
    if type(value['author']) is list:
        text = []
        for author in value['author']:
            if type(author) is str:
                text.append(author)
            else:
                text.append(author['#text'])
        
        return ', '.join(text)    

    # Only one dict case
    return value['author']['#text']

def main(min_year=float("-inf"), max_year=float("inf")):
    output = []
    authors_dict = {author: [] for author in AUTHORS}
    pbar_out = tqdm(unit=' entries', unit_scale=True, total=DBLP_SIZE)
    pbar_in = tqdm(unit=' articles', unit_scale=True)
    count = 0
    
    try:
        with open(PATH_TO_MARSHAL, 'rb') as f:
            while True:
                try:
                    info, value = marshal.load(f)

                    # Check if we should insert this
                    if info[1][0] == 'inproceedings' and \
                        float(value['year']) >= min_year and \
                        float(value['year']) <= max_year:

                        # Check, for each author, if it should be added
                        for author in authors_dict.keys():
                            if re.compile(author).search(get_authors(value)):
                                authors_dict[author].append(value)
                                tqdm.write("[INFO] Added to {}".format(author))
                        
                        pbar_in.update(1)
                except KeyError as e:
                    pass
                except EOFError as e:
                    break
                pbar_out.update(1)
                count += 1
    finally:
        pbar_out.close()
        pbar_in.close()

    for author in authors_dict.keys():
        with open(AUTHORS_FOLDER + '_'.join(author.replace('.', '').split(' ')) + '.json', 'w') as f:
            json.dump(authors_dict[author], f, indent=2)

    print("Final count", count)

# Calling main with fire
if __name__ == "__main__":
    fire.Fire(main)
