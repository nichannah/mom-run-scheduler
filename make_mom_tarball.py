#!/usr/bin/env python

from __future__ import print_function

import os, sys
import argparse

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--mom_version', default='6',
                        help='MOM version, use 5 or 6')
    args = parser.parse_args()


if __name__ == '__main__':
    sys.exit(main())
