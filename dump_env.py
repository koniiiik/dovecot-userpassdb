#!/usr/bin/env python

import json
import os


def main():
    with os.fdopen(4, 'w') as f:
        json.dump(dict(os.environ), f)

if __name__ == "__main__":
    main()
