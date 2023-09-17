#!/usr/bin/env python3
from weekly_markdown.util import Util


def main() -> None:
    """
    TODO
    """
    filename = "./src/config.yaml"
    util = Util(filename)

    util.run()

if __name__ == "__main__":
    main()
