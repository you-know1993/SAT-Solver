import math
import os
import re
import sys
from typing import List, IO


def main(sudoku_filename: str, output_directory: str, output_prefix: str) -> None:
    # Opens the file.
    input_file: IO = open(sudoku_filename, "r")
    # Iterates over every line, creating a sudoku of each line in the file.
    for i, sudoku in enumerate(input_file):
        # Remove all characters that we don't need.
        sudoku: str = re.sub('[^1-9A-Z.]', '', sudoku)
        size: float = math.sqrt(len(sudoku))
        if not size.is_integer():
            print("Sudoku '{0}' does not have square dimensions.".format(sudoku))
            continue

        # How many digits will we need to encode the variables in decimals.
        num_digits: int = math.ceil(math.log10(int(size) + 1))
        # List to store the clauses in
        clauses: List[List[str]] = []
        counter: int = 0
        current_col: int = int(size)
        current_row: int = 0

        # Iterates over every character in the line, making it a clause if it's a number.
        for character in sudoku:
            if current_col == size:
                current_row += 1
                current_col: int = 0
                # This will resolve to 100 for 1 digit or 10.000 for 2 digits.
                counter: int = int(math.pow(10, num_digits * 2) * current_row)

            current_col += 1
            counter += int(math.pow(10, num_digits))

            # Determines if it's a useable clause.
            if character != '.':
                # The ordinal value of the first letter, A, is 65, but will be the 10th character in our notation.
                literal: int = counter + (int(character) if character.isnumeric() else (ord(character.lower()) - 55))
                clauses.append([str(literal)])

        # Write the clauses to a cnf file.
        output_filename: str = os.path.join(output_directory, output_prefix + '-' + str(i).rjust(4, '0') + '.txt')
        output_file: IO = open(output_filename, 'w')
        output_file.write("p cnf {} {}\n".format(str(int(size)) * 3, len(clauses)))
        for clause in clauses:
            output_file.write(" ".join(clause) + " 0\n")
        output_file.close()


main(sys.argv[1], sys.argv[2], sys.argv[3])