import json
import marshal
from sklearn.feature_extraction.text import TfidfVectorizer
import fire
import pprint

def fetch_title(entry):
    return entry['title'] if type(entry['title']) is str else entry['title']['#text']

def main(conferences_input_file = 'dblp.json', author_input_file = 'author_dblp.json'):
    
    # Read conferences file
    with open(conferences_input_file, 'r') as f:
        conferences_json_dict = json.load(f)

    conferences_corpus = [fetch_title(entry) for entry in conferences_json_dict]
    pprint.pprint(conferences_corpus)

    # Read author file
    with open(author_input_file, 'r') as f:
        author_json_dict = json.load(f)

    author_corpus = [fetch_title(entry) for entry in author_json_dict]
    pprint.pprint(author_corpus)

    # Run TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(conferences_corpus)
    pprint.pprint(X)



if __name__ == "__main__":
    fire.Fire(main)