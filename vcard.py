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

    def __init__(self, _lines):
        print("# =========================================")
        accumulator_key = None
        accumulator_value = None
        for _line in _lines:
            # print(f"# {_line}")
            if not _line.startswith(" "):
                matches = re.match(r"^(.+):(.+)$", _line)
                if matches:
                    key = matches.groups()[0]
                    value = matches.groups()[1]
                    if accumulator_key is not None:
                        print(f"KEY1: {accumulator_key} VALUE: {accumulator_value}")
                        accumulator_key = None
                        accumulator_value = None
                    if key.startswith("PHOTO") or key.startswith("item"):
                        accumulator_key = key
                        accumulator_value = [value]
                    else:
                        print(f"KEY2: {key} VALUE: {value}")
            else:
                accumulator_value.append( _line.strip())

            # if _line.startswith("VERSION:"):
            #     self.full_name = _line[3:]
            # elif _line.startswith("N:"):
            #     self.family_name, self.given_name, self.middle_name, self.prefix, self.suffix = _line[2:].split(";")
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
        for line in self.lines:
            if line == "BEGIN:VCARD":
                lines = []
                lines.append(line)
            elif line == "END:VCARD":
                if lines is None:
                    raise ValueError("Error: END:VCARD found without a corresponding BEGIN:VCARD")
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
    vcards = vCards(in_file)
    num_records = vcards.split_records_lines()
    print(f"Number of records: {num_records}")
    vcards.process_records_lines()
    # print(vcards)
    # vcards.process_record_lines()

