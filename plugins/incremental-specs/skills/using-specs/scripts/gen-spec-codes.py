#!/usr/bin/env python3
"""Generate random statement codes for reference specs.

Each code is 5 lowercase alphanumeric characters with at least one letter and
one digit, e.g. '2b342', so it reads as a random code rather than a word or a
number. Codes tag behavior statements in reference specs; see the using-specs
skill.
"""

from __future__ import annotations

import argparse
import secrets
import string

CODE_LENGTH = 5
ALPHABET = string.ascii_lowercase + string.digits


def gen_code() -> str:
    while True:
        code = "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))
        if any(c.isalpha() for c in code) and any(c.isdigit() for c in code):
            return code


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "-k",
        type=int,
        default=1,
        metavar="N",
        help="number of codes to generate (default: 1)",
    )
    args = parser.parse_args()
    if args.k < 1:
        parser.error("-k must be at least 1")

    codes: list[str] = []
    seen: set[str] = set()
    while len(codes) < args.k:
        code = gen_code()
        if code in seen:
            continue
        seen.add(code)
        codes.append(code)
    print("\n".join(codes))


if __name__ == "__main__":
    main()
