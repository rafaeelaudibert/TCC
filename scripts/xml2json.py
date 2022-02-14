from gzip import GzipFile
import click
import jsonstreams
import xmltodict
from tqdm import tqdm

ESTIMATED_TOTAL = 8950000  # Estimated looking at previous .json files


@click.command()
@click.argument("input_filename", type=click.Path(exists=True))
@click.argument("output_filename", type=click.Path(writable=True))
def main(input_filename, output_filename):
    """
    Attempts to stream a .XML.GZ file from INPUT_FILENAME,
    outputting an equivalent JSON file to OUTPUT_FILENAME
    """

    tqdm_handler = tqdm(desc="XML Parsing (Estimated)", total=ESTIMATED_TOTAL)
    output_stream = jsonstreams.Stream(
        jsonstreams.Type.ARRAY,
        filename=output_filename,
        pretty=True,
        indent=2,
    )

    def handle_entry(_, entry):
        output_stream.write(entry)
        tqdm_handler.update()

        return True

    xmltodict.parse(GzipFile(input_filename), item_depth=2, item_callback=handle_entry)

    # Remember to close the open fd-like instances at the end of the execution
    output_stream.close()
    tqdm_handler.close()


if __name__ == "__main__":
    main()
