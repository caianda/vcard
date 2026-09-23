#!/usr/bin/env python

import json
import re

from file_utils import read_txt_file

# ----------------------------------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------------------------------
# in_file = "sample_apple.vcf"
in_file = "test.vcf"

filename = "google_contacts.csv"

# ----------------------------------------------------------------------------------------------------
# Supporting Functions
# ----------------------------------------------------------------------------------------------------

CYAN = "\033[36m"
RESET = "\033[0m"
RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"


class Contact:

    def __init__(self, first_name, last_name):
        self.given_name = None
        self.family_name = None
        self.middle_name = None
        self.prefix = None
        self.suffix = None
        self.email_home = None
        self.email_work = None
        self.email_school = None
        self.phone_home = None
        self.phone_work = None

    def to_json(self):
        return {
            "family_name": getattr(self, "family_name", None),
            "given_name": getattr(self, "given_name", None),
            "middle_name": getattr(self, "middle_name", None),
            "prefix": getattr(self, "prefix", None),
            "suffix": getattr(self, "suffix", None),
            "email_home": getattr(self, "email_home", None),
            "email_work": getattr(self, "email_work", None),
            "email_school": getattr(self, "email_school", None),
            "phone_home": getattr(self, "phone_home", None),
            "phone_work": getattr(self, "phone_work", None),
        }

    def __str__(self):
        return repr(self)
        # return json.dumps(self.to_json(), indent=4, sort_keys=True)


class vCard(Contact):

    @staticmethod
    def extract_key(_key_str):
        if _key_str in ["BEGIN", "END", "VERSION", "N", "FN", "PRODID", "REV"]:
            return _key_str
        elif _key_str.startswith("PHOTO") or _key_str.startswith("BDAY"):
            return _key_str
        elif matches := re.match(r"^(item\d+)", _key_str):
            return matches.group(1)
        raise ValueError(f"Unrecognized key: {_key_str}")

    def __init__(self, _lines):
        print("# =========================================")
        accumulator_key = None
        accumulator_value = None
        for _line in _lines:
            print("\n>> ", _line)
            matches = re.match(r"^(.+):(.+)$", _line)
            if matches:
                key_str = matches.groups()[0]
                value = matches.groups()[1]
                key = vCard.extract_key(key_str)
                print(f"KEY0: {key_str}=>{key} VALUE: {value}")
            else:
                print(f"NO MATCH: {_line}")
            # # print(f"# {_line}")
            # if accumulator_key is None:
            #     if accumulator_key is not None:
            #         print(f"KEY1: {accumulator_key} VALUE: {accumulator_value}")
            #         accumulator_key = None
            #         accumulator_value = None
            #     if key.startswith("PHOTO") or key.startswith("item"):
            #         accumulator_key = key
            #         accumulator_value = [value]
            #     else:
            #         print(f"KEY2: {key} VALUE: {value}")
            # else:
            #     if accumulator_value is not None:
            #         accumulator_value.append(_line.strip())

            # # if _line.startswith("VERSION:"):
            # #     self.full_name = _line[3:]
            # # elif _line.startswith("N:"):
            # #     self.family_name, self.given_name, self.middle_name, self.prefix, self.suffix = _line[2:].split(";")


#         items = {}
#         for line in _lines:
#             if line.startswith("FN:"):
#                 pass
#             elif line.startswith("N:"):
#                 self.family_name, self.given_name, self.middle_name, self.prefix, self.suffix = line[2:].split(";")
#             elif matches := re.match(r"^item(\d+)", line):
#                 if matches.group(1) not in items:
#                     items[matches.group(1)] = [line ]
#                     print("FIRST: ", items)
#                 else:
#                     items[matches.group(1)].append(line)
#                     print("SECOND",items)
#                     print(repr(self))
#                     self.process_item(items[matches.group(1)])
#                     self.__setattr__(f"phone_work", "123123123")
#                     print("HERE")
#                     print(repr(self))


#         vCard.vcards.append(self)

#     def process_item(self, item_lines):
#         item_number = None
#         item_type = None
#         item_value = None
#         item_label = None
#         for line in item_lines:
#             if matches := re.match(r"^item(\d+)\.(\w+);.*:(.*)$", line):
#                 item_number = matches.group(1)
#                 item_type = matches.group(2).lower()
#                 item_value = matches.group(3)
#                 print(f"Item {item_number} [{item_type}] Value: {item_value}")
#             elif matches := re.match(r"^item(\d+)\.X-ABLabel:(.*)$", line):
#                 item_number = matches.group(1)
#                 item_label = matches.group(2)
#                 self.__setattr__(f"{item_type.lower()}_{item_label.lower()}", item_value)
#                 print(f"Item {item_number} [{item_type}] Label: {item_label} Value: {item_value}")
#             else:
#                 raise ValueError(f"Unrecognized item line: {line}")
#         print("SELF=", self)

#     def __str__(self):
#         return super().__str__()
#         # return super().__str__() + "\n" + "vCard: " + self.given_name + " " + self.family_name


class vCards:

    def __init__(self, _filename):
        self.lines = read_txt_file(_filename)
        self.records_lines = []
        # self.split_record_lines()

    def split_records_lines(self) -> int:
        lines = None
        if self.lines is None:
            return 0
        for line in self.lines:
            if line == "BEGIN:VCARD":
                lines = []
                lines.append(line)
            elif line == "END:VCARD":
                if lines is None:
                    raise ValueError(
                        "Error: END:VCARD found without a corresponding BEGIN:VCARD"
                    )
                elif lines == []:
                    raise ValueError("Error: END:VCARD immediately after BEGIN:VCARD")
                else:
                    lines.append(line)
                    self.records_lines.append(lines)
                    lines = None
            else:
                if lines is not None:
                    lines.append(line)
        self.lines = None
        return len(self.records_lines)

    def process_records_lines(self):
        for record_lines in self.records_lines:
            vcard = vCard(record_lines)
            # print(vcard)

    def __str__(self):
        for i, record in enumerate(self.records_lines):
            print("# =========================================")
            print("# Record: ", i + 1)
            print("# =========================================")
            for line in record:
                print(f"{line}")
        return f"vCards: {len(self.records_lines)} records"


# ----------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    # vcards = vCards(in_file)
    # num_records = vcards.split_records_lines()
    # print(f"Number of records: {num_records}")
    # vcards.process_records_lines()
    # # print(vcards)
    # # vcards.process_record_lines()

    lines = read_txt_file(in_file)

    records = []
    record = None
    current_key = None
    # lines = read_txt_file(in_file)
    for line in lines:
        # qline = re.sub(r"([\n]+)", r"\\n", re.sub(r"([\r]+)", r"\\r", line))
        print(f"\n{CYAN}>>{line}{RESET}")
        if re.match(r"^\s*$", line):
            continue
        elif line == "BEGIN:VCARD":
            record = {}
        elif line == "END:VCARD":
            records.append(record)
            record = None
        elif line.startswith(" "):
            if record is not None and current_key is not None:
                record[current_key][-1] += line[1:]
                print(
                    f"{MAGENTA}>> Continuation for key: {current_key} = {record[current_key][-1]}{RESET}"
                )
                # break
        elif matches := re.match(r"^([^:]+):(.+)", line):
            key, value = matches.groups()
            if record is None:
                print(
                    f"{RED}!! Record is None when trying to add key: {key}, value: {value}{RESET}"
                )
                raise ValueError(
                    f"Record is None when trying to add key: {key}, value: {value}"
                )
            record[key] = [value]
            current_key = key
        else:
            print(f"{YELLOW}!! Unrecognized line: {line}{RESET}")

    print("# -----------------------------------------------")
    print(f"{CYAN}Parsed records:{RESET}")
    print(json.dumps(records, indent=4))
