import json
import click


@click.command()
@click.argument("input", type=click.File("r"))
@click.argument("output", type=click.File("w"))
def main(input, output):
    """
    Opens the [INPUT] (which must be a JSON) and sorts it alphabetically
    by its value (and then by key).
    Then stores in on [OUTPUT]
    Make sure [INPUT] and [OUTPUT] are not the same file
    """
    data = json.load(input)

    sorted_items = sorted(data.items(), key=lambda item: (item[1] or "", item[0]))
    sorted_data = {key: value for key, value in sorted_items}

    json.dump(sorted_data, output, indent=2)


if __name__ == "__main__":
    main()
