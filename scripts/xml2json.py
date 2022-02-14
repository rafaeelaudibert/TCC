from gzip import GzipFile
import click
from streamxml2json import stream_xml2json

ESTIMATED_TOTAL = 8950000  # Estimated looking at previous .json files


@click.command()
@click.argument("input_filename", type=click.Path(exists=True))
@click.argument("output_filename", type=click.Path(writable=True))
def main(input_filename, output_filename):
    """
    Attempts to stream a .XML.GZ file from INPUT_FILENAME,
    outputting an equivalent JSON file to OUTPUT_FILENAME
    """

    gzip_file = GzipFile(input_filename)
    tqdm_kwargs = {"total": ESTIMATED_TOTAL}

    stream_xml2json(
        gzip_file,
        output_filename,
        item_depth=2,
        pretty=True,
        indent=2,
        tqdm_kwargs=tqdm_kwargs,
    )
    gzip_file.close()


if __name__ == "__main__":
    main()
