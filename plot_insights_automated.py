import json
import marshal
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import mean_squared_error, r2_score
from sklearn import linear_model
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import fire
import pprint
from ordered_set import OrderedSet
from tqdm import tqdm, trange

CONFERENCES_BASE_PATH = './conferences/'
AUTHORS_BASE_PATH = './turing_awards/'
IMAGE_FOLDER_PATH = './img/'
AUTOMATION_FILE = 'turing_awards_vs_conferences.json'


def fetch_title(entry: dict):
    """
    Fetch the title from an entry from the json file
    This function is needed because as the json was parsed from an XML, some
    fields aren't correctly parsed
    """
    return entry['title'] if type(entry['title']) is str else entry['title']['#text']   # nopep8


def main():

    # Parse the automation file querying the data
    with open(AUTOMATION_FILE, 'r') as f:
        # Read the plots asked from the file
        iterable_plots = json.load(f)

        # Read conferences file, and parse their corpus
        # by year and in its entirety
        for plot in tqdm(iterable_plots):

            # Fetching conferences corpus
            conferences_corpus_by_year = {}
            for conference_path in plot['conferences']:
                with open(CONFERENCES_BASE_PATH + conference_path, 'r') as f:
                    full_data = json.load(f)
                    for entry in full_data:
                        if 'start_year' not in plot or int(entry['year']) > plot['start_year']:  # nopep8
                            if entry['year'] not in conferences_corpus_by_year:
                                conferences_corpus_by_year[entry['year']] = {
                                    'corpus': []}

                            conferences_corpus_by_year[entry['year']]['corpus'].append(   # nopep8
                                fetch_title(entry))

            # Fetching authors corpus
            author_corpus = []
            for author_path in plot['turing_awards']:
                with open(AUTHORS_BASE_PATH + author_path, 'r') as f:
                    author_corpus += [fetch_title(entry)
                                      for entry in json.load(f)]

            # Run TF-IDF, averaging it for each feature
            # for the conference years
            for year in conferences_corpus_by_year.keys():
                vectorizer = TfidfVectorizer(stop_words='english')
                conferences_corpus_by_year[year]['tf-idf'] = vectorizer.fit_transform(   # nopep8
                    conferences_corpus_by_year[year]['corpus'])
                conferences_corpus_by_year[year]['mean-tf-idf'] = sorted(list(zip(conferences_corpus_by_year[year]['tf-idf'].mean(   # nopep8
                    0).transpose(), vectorizer.get_feature_names())), key=lambda x: x[0], reverse=True)   # nopep8

            # Run TF-IDF, averaging it for each feature for the author papers
            vectorizer = TfidfVectorizer(stop_words='english')
            author_corpus_dict = {}
            author_corpus_dict['tf-idf'] = vectorizer.fit_transform(
                author_corpus)
            author_corpus_dict['mean-tf-idf'] = sorted(list(zip(author_corpus_dict['tf-idf'].mean(   # nopep8
                0).transpose(), vectorizer.get_feature_names())),
                key=lambda x: x[0], reverse=True)

            # Computing Spearman's correlation for each year conference corpus
            plot_data = {}
            for year in sorted(conferences_corpus_by_year.keys()):
                conference_ranking = [
                    entry[1] for entry in conferences_corpus_by_year[year]['mean-tf-idf']]   # nopep8
                author_ranking = [entry[1]
                                  for entry in author_corpus_dict['mean-tf-idf']]   # nopep8

                conference_ranking_set = OrderedSet(conference_ranking)
                author_ranking_set = OrderedSet(author_ranking)
                intersected_set = author_ranking_set.intersection(
                    conference_ranking_set)

                intersected_conference_ranking = [conference_ranking_set.index(
                    intersection) for intersection in intersected_set]
                intersected_author_ranking = [author_ranking_set.index(
                    intersection) for intersection in intersected_set]

                sc, p = stats.spearmanr(
                    intersected_author_ranking, intersected_conference_ranking)
                plot_data[year] = sc

            # Create regression object + computing it
            X = np.array([int(x) for x in plot_data.keys()]).reshape(-1, 1)
            Y = list(plot_data.values())

            # Clear plot
            plt.clf()

            # Plotting data and saving to file
            # Plot linear regression line
            try:
                regr = linear_model.LinearRegression()
                regr.fit(X, Y)
                Y_pred = regr.predict(X)
                plt.plot(X, Y_pred, color='blue', linewidth=2)
            except ValueError as _:
                pass

            # Plot dashed line at 0.0
            plt.plot([min(X), max(X)], [0, 0], dashes=[
                     15, 5, 15, 5], linewidth=0.5)

            # Plot start on award year
            if plot['award_year'] is not None and str(plot['award_year']) in plot_data:   # nopep8
                plt.scatter([plot['award_year']], [
                            plot_data[str(plot['award_year'])]],
                            c='orange',
                            marker='*',
                            s=500)

            # Plot data
            plt.scatter(X, Y, color='green')

            # Plot title
            plt.title(plot['title'])

            # Configure limit
            plt.ylim([min(-0.1, min(Y)), max(0.8, max(Y))])

            # Save image to folder
            plt.savefig(IMAGE_FOLDER_PATH + plot['title'] + '.png')

            tqdm.write('Finished {}'.format(plot['title']))


if __name__ == "__main__":
    main()
