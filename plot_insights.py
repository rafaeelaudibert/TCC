import json
import marshal
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import matplotlib.pyplot as plt
import fire
import pprint

CONFERENCES_BASE_PATH = './conferences/'
AUTHORS_BASE_PATH = './turing_awards/'

def fetch_title(entry):
    return entry['title'] if type(entry['title']) is str else entry['title']['#text']

def main(conferences_input_file = 'dblp.json', author_input_file = 'author_dblp.json'):
    
    # Read conferences file
    print('[INFO] Fetching conferences corpus')
    with open(CONFERENCES_BASE_PATH + conferences_input_file, 'r') as f:
        conferences_corpus = [fetch_title(entry) for entry in json.load(f)]

    # Read author file
    print('[INFO] Fetching author corpus')
    with open(AUTHORS_BASE_PATH + author_input_file, 'r') as f:
        author_corpus = [fetch_title(entry) for entry in json.load(f)]

    # Compute full corpus
    print('[INFO] Computing full corpus')
    full_corpus = conferences_corpus + author_corpus

    # Run TF-IDF
    print('[INFO] Computing TF-IDF for the full corpus')
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(full_corpus)
    pprint.pprint(X)

    # Run Singular Value Decomposition
    print('[INFO] Computing SVD in the TF-IDF')
    svd = TruncatedSVD()
    svd.fit(X)
    pprint.pprint(svd.components_)

    # Plotting scattered data
    plt.scatter(*svd.components_)
    plt.show()



if __name__ == "__main__":
    fire.Fire(main)