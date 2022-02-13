# TODO: Understand what this file was for

import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import linear_model
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import click
import pprint
from ordered_set import OrderedSet

IMAGE_FOLDER_PATH = "./img/"


def fetch_title(entry: dict):
    return entry["title"] if type(entry["title"]) is str else entry["title"]["#text"]


@click.command()
@click.argument("plot_title")
@click.option(
    "--conferences-input-file",
    default="./conferences/dblp.json",
    show_default=True,
    help="File which we load our data from",
    type=click.File(),
)
@click.option(
    "--author-input-files",
    multiple=True,
    default=["./turing_awards/author_dblp.json"],
    show_default=True,
    help="Basepath where we will store the images on",
    type=click.Path(exists=True),
)
@click.option("--award-year", help="Optional value to show when an award was won", type=int)
def main(plot_title, conferences_input_file, author_input_files, award_year):

    # Read conferences file, and parse their corpus by year and in its entirety
    print("[INFO] Fetching conferences corpus")
    conferences_corpus_by_year = {}
    with open(conferences_input_file, "r") as f:
        full_data = json.load(f)
        for entry in full_data:
            if entry["year"] not in conferences_corpus_by_year:
                conferences_corpus_by_year[entry["year"]] = {"corpus": []}

            conferences_corpus_by_year[entry["year"]]["corpus"].append(fetch_title(entry))

    # Read author file
    print("[INFO] Fetching author(s) corpus")
    author_corpus = []
    for author_path in author_input_files:
        with open(author_path, "r") as f:
            author_corpus += [fetch_title(entry) for entry in json.load(f)]

    # Run TF-IDF, averaging it for each feature for the conference years
    print("[INFO] Computing TF-IDF for the conferences corpus")
    for year in conferences_corpus_by_year.keys():
        vectorizer = TfidfVectorizer(stop_words="english")
        conferences_corpus_by_year[year]["tf-idf"] = vectorizer.fit_transform(
            conferences_corpus_by_year[year]["corpus"]
        )
        conferences_corpus_by_year[year]["mean-tf-idf"] = sorted(
            list(
                zip(
                    conferences_corpus_by_year[year]["tf-idf"].mean(0).transpose(),
                    vectorizer.get_feature_names(),
                )
            ),
            key=lambda x: x[0],
            reverse=True,
        )

    # Run TF-IDF, averaging it for each feature for the author papers
    print("[INFO] Computing TF-IDF for the author corpus")
    vectorizer = TfidfVectorizer(stop_words="english")
    author_corpus_dict = {}
    author_corpus_dict["tf-idf"] = vectorizer.fit_transform(author_corpus)
    author_corpus_dict["mean-tf-idf"] = sorted(
        list(zip(author_corpus_dict["tf-idf"].mean(0).transpose(), vectorizer.get_feature_names())),
        key=lambda x: x[0],
        reverse=True,
    )

    # Calculating the Spearman's correlation for each year
    print("[INFO] Computing Spearman's correlation for each year conference corpus")
    plot_data = {}
    for year in sorted(conferences_corpus_by_year.keys()):
        conference_ranking = [entry[1] for entry in conferences_corpus_by_year[year]["mean-tf-idf"]]
        author_ranking = [entry[1] for entry in author_corpus_dict["mean-tf-idf"]]

        conference_ranking_set = OrderedSet(conference_ranking)
        author_ranking_set = OrderedSet(author_ranking)
        intersected_set = author_ranking_set.intersection(conference_ranking_set)

        intersected_conference_ranking = [
            conference_ranking_set.index(intersection) for intersection in intersected_set
        ]
        intersected_author_ranking = [author_ranking_set.index(intersection) for intersection in intersected_set]

        sc, p = stats.spearmanr(intersected_author_ranking, intersected_conference_ranking)
        plot_data[year] = sc

    pprint.pprint(plot_data)

    # Create regression object + computing it
    print("[INFO] Computing linear regression")
    X = np.array([int(x) for x in plot_data.keys()]).reshape(-1, 1)
    Y = list(plot_data.values())
    regr = linear_model.LinearRegression()
    regr.fit(X, Y)
    Y_pred = regr.predict(X)

    # Plotting scattered data
    print("[INFO] Plotting data")
    plt.plot(X, Y_pred, color="blue", linewidth=3)
    if award_year is not None:
        plt.scatter([award_year], [plot_data[str(award_year)]], c="orange", marker="*", s=500)
    plt.scatter(X, Y, color="green")
    plt.title(plot_title)
    plt.savefig(IMAGE_FOLDER_PATH + plot_title + ".png")
    # plt.show()


if __name__ == "__main__":
    main()
