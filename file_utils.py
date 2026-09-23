#!/usr/bin/env python
# --------------------------------------------------------------------------------------
# File I/O Utilities
# Written by Andrew Toy <andrew.toy@caianda.com>
# --------------------------------------------------------------------------------------

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

# --------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------
# Supporting Functions
# --------------------------------------------------------------------------------------


def file_exists(_filename):
    return os.path.exists(_filename)


def rename_file(_old_filename, _new_filename) -> bool:
    if file_exists(_new_filename):
        return False
    os.rename(_old_filename, _new_filename)
    return True


def read_txt_file(_filename):
    """
    read_file reads a text file into an array of lines

    :params _filename: string containing the name of the file to read
    :return: array of lines
    """
    _lines = []
    try:
        with open(_filename, "r", encoding="utf-8") as reader:
            for line in reader.readlines():
                _lines.append(re.sub("[\r\n]+$", "", line))
    finally:
        reader.close()
    return _lines


def write_txt_file(_filename, _lines):
    """
    write_file will output the provided lines to a file

    :param _filename: name of the file to write
    :param _lines: an array of strings (without CR-LF)
    :return: None
    """
    try:
        with open(_filename, "w") as writer:
            for line in _lines:
                writer.write(line + "\n")
    finally:
        writer.close()


def append_txt_file(_filename, _lines):
    """
    append_file will output the provided lines to a file
    :param _filename: name of the file to write
    :param _lines: an array of strings (without CR-LF)
    :return: None
    """
    try:
        with open(_filename, "a") as writer:
            for line in _lines:
                writer.write(line + "\n")
    finally:
        writer.close()


def read_csv_file(
    _filename, _delimiter=None, _field_size_limit=None, _create_hash=False
):
    """
    read csv and parse into rows / columns

    :param _filename: string containing the name of the CSV file to read
    :param _delimiter: optional string containing the delimiter to split the file
    :param _field_size_limit: optional string containing the delimiter to split the file
    :param _create_hash: optional flag to indicate whether user wants a hash returned instead of
             a 2-D array
    :return: 2-dimensional array containing parsed contents of CSV file, e.g.
             [ [ r1c1, r1c2, r1c3 ], [ r2c1, r2c2, r2c3 ] ... ]
             or [ { "r1c1": "r2c1",  "r1c2": "r2c2",  "r1c3": "r2c3" } ... ]
    """
    import csv

    if _delimiter is None:
        if re.match("^.+\\.csv$", str(_filename)):
            _delimiter = ","
        elif re.match("^.+\\.psv$", str(_filename)):
            _delimiter = "|"
        elif re.match("^.+\\.tsv$", str(_filename)):
            _delimiter = "\t"

    if _field_size_limit is not None and _field_size_limit == 0:
        max_int = sys.maxsize
        csv.field_size_limit(max_int)

    headings = None
    rows = []
    with open(_filename, mode="r") as file:
        _lines = csv.reader(file, delimiter=_delimiter, quotechar='"', dialect="unix")
        headings = []
        linenum = 0
        for line in _lines:
            linenum += 1
            if linenum == 1:
                # rows.append(list(map(lambda x: x.replace("\ufeff", ""), line)))
                # rows.append([x.replace("\ufeff", "") for x in line])
                # headings = rows[0]
                headings = [x.replace("\ufeff", "") for x in line]
                if _create_hash is False:
                    rows.append(headings)
            else:
                if _create_hash:
                    row_dict = dict(zip(headings, line))
                    rows.append(row_dict)
                else:
                    rows.append(line)
        file.close()
    return rows


def write_csv_file(_filename, _rows, _delimiter=","):
    """
    write_file will output the provided lines to a file

    :param _filename: name of the file to write
    :param _rows: an array of array-of-strings (without CR-LF)
    :param _delimiter: specifies the delimiter for the csv file
    :return: None
    """
    import csv

    with open(_filename, "w") as file:
        writer = csv.writer(
            file,
            delimiter=_delimiter,
            quotechar='"',
            quoting=csv.QUOTE_ALL,
            dialect="unix",
        )
        writer.writerows(_rows)
        file.close()


def read_json_file(_filename, _debug=False) -> dict:
    """
    read json file into a dictionary

    :param _filename: string containing the name of the JSON file to read
    :return: dictionary containing the data read from the JSON file
    """

    try:
        _lines = read_txt_file(_filename)
        if _debug:
            print(f"_lines    = {_lines}")
        _line_str = "\n".join(_lines)
        if _debug:
            print(f"_line_str = {_line_str}")
        _dict = json.loads(_line_str)
        if _debug:
            print(f"_dict     = {_dict}")
    except Exception as e:
        print(f"Error reading JSON file {_filename}: {e}")
        _dict = {}
    return _dict


def write_json_file(_filename, _dictionary):
    """
    write dictionary into a json file

    :param _filename: string containing the name of the JSON file to read
    :param _dictionary: dict containing the data to be written to JSON file

    :return: None
    """
    _lines = [json.dumps(_dictionary, indent=2)]
    write_txt_file(_filename, _lines)


def parse_datestring(datestr):
    """
    Parse a datestring or timestamp into a datetime.datetime object.

    Supported inputs:
    - datetime.datetime (returned unchanged)
    - int/float (treated as a POSIX timestamp in seconds)
    - numeric string of seconds or milliseconds since epoch
    - ISO 8601 strings (YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, with optional TZ)
    - common formats: MM/DD/YYYY, DD/MM/YYYY, with optional time
    - if python-dateutil is available, falls back to dateutil.parser.parse

    Returns a datetime.datetime. If the parsed value contains timezone info,
    that tzinfo is preserved; otherwise a naive datetime is returned.
    """
    if datestr is None:
        raise ValueError("datestr is None")

    # already a datetime
    if isinstance(datestr, datetime):
        return datestr

    # numeric input
    if isinstance(datestr, (int, float)):
        return datetime.fromtimestamp(float(datestr))

    s = str(datestr).strip()

    # pure digits: seconds or milliseconds
    if re.fullmatch(r"\d+", s):
        # heuristics: >=13 digits -> milliseconds
        if len(s) >= 13:
            ts = int(s) / 1000.0
        else:
            ts = int(s)
        return datetime.fromtimestamp(ts)

    # try fromisoformat (accepts 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS')
    try:
        return datetime.fromisoformat(s)
    except Exception:
        pass

    # try a list of common strptime formats
    fmts = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
        "%Y%m%d",
    ]
    for f in fmts:
        try:
            return datetime.strptime(s, f)
        except Exception:
            continue

    # fallback to dateutil if available
    try:
        from dateutil import parser as _parser

        return _parser.parse(s)
    except Exception:
        pass

    raise ValueError(f"Unrecognized date format: {datestr}")


def read_binary_file(_filename):
    """
    read_file reads a binary file into bytes

    :params _filename: string containing the name of the file to read
    :return: bytes
    """
    try:
        with open(_filename, "rb") as reader:
            _data = reader.read()
    finally:
        reader.close()
    return _data


def write_binary_file(_filename, _data):
    """
    write_file will output the provided bytes to a binary file

    :param _filename: name of the file to write
    :param _data: bytes to write to the file
    :return: None
    """
    try:
        with open(_filename, "wb") as writer:
            writer.write(_data)
    finally:
        writer.close()


def unzip_file(_zip_path, _output_dir, _password=None):
    """
    unzip_file will unpack a .zip file into the output directory
    with an optional password if the file is encrypted

    :param _zip_path: path to the zip file
    :param _output_dir: directory to extract the contents to
    :param _password: optional password for encrypted zip files
    :return: None
    """
    import pyzipper

    # Extracting the encrypted ZIP file
    if _output_dir is not None and not os.path.exists(_output_dir):
        os.makedirs(_output_dir)
    with pyzipper.AESZipFile(_zip_path, "r") as zip_ref:
        zip_ref.pwd = _password
        zip_ref.extractall(_output_dir)


def table_to_dict(_table, _debug=False):
    """
    Convert a list of dictionaries (table) into a dictionary keyed by a specified field.
    Assumes that the first row contains the headings.

    :param _table: List of dictionaries representing the table., e.g.
        [ [ r1c1, r1c2, r1c3 ], [ r2c1, r2c2, r2c3 ], [ r3c1, r3c2, r3c3 ] ]
    :param _debug: If True, print debug information
    :return: Dictionary keyed by the header column in the first row, e.g.
        [
            {'r1c1': 'r2c1', 'r1c2': 'r2c2', 'r1c3': 'r2c3'},
            {'r1c1': 'r3c1', 'r1c2': 'r3c2', 'r1c3': 'r3c3'}
        ]
    """
    headings = _table[0]
    rows = []
    for row in _table[1:]:
        if _debug:
            print(row)
        if len(row) == len(headings):
            cols = dict(zip(headings, row))
            for k, v in cols.items():
                if v is not None and len(str(v).strip()) == 0:
                    v = None
                    cols[k] = v
            rows.append(cols)
        else:
            raise ValueError("Row length does not match headings length")
    return rows


if __name__ == "__main__":
    print("File Utils")
