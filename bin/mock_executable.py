#!/usr/bin/env python

import time
import shutil
import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input_json')
    parser.add_argument('-o', '--output_json')

    args = parser.parse_args()

    print("copying %s to %s" % (args.input_json,
                                args.output_json))

    time.sleep(
        int(
            os.environ.get('SLEEPTIME', '60')
        )
    )

    print("done")

    shutil.copy(args.input_json,
                args.output_json)
