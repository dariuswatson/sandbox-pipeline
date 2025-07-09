import csv
import os


def write_dicts_to_csv(data, filename):
    """
    Appends a list of dictionaries to a CSV file. Writes headers only if file is new or empty.

    Args:
        data (list of dict): The data to write.
        filename (str): Name of the CSV file to append to.
    """
    if not data:
        print("No data to write.")
        return

    if not isinstance(data, list) or not isinstance(data[0], dict):
        raise ValueError("Data must be a list of dictionaries.")

    fieldnames = data[0].keys()
    file_exists = os.path.isfile(filename)
    write_header = not file_exists or os.path.getsize(filename) == 0

    with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=fieldnames,
                                quoting=csv.QUOTE_ALL,  # Quote all fields
                                escapechar='\\',  # Escape special characters like backslashes
                                quotechar='"',
                                )

        if write_header:
            writer.writeheader()

        writer.writerows(data)



