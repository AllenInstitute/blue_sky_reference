#!/usr/bin/env python

import time
import shutil
import argparse
import simplejson as json
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input_json')
    parser.add_argument('-o', '--output_json')

    args = parser.parse_args()

    time.sleep(
        int(
            os.environ.get('SLEEPTIME', '60')
        )
    )

    job_queue = os.environ.get('BLUE_SKY_JOB_QUEUE', 'Copy Input')

    if job_queue == 'Generate Lens Correction Transform':
        with open(args.output_json, 'w') as f:
            json.dump(
                {
                    'output_json': '/green/mock_output_file.json',
                    'maskUrl': 'http://example.org/mask'
                },
                f)
    elif job_queue == 'Create Tile Pairs':
        with open(args.output_json, 'w') as f:
            json.dump(
                {
                    'tile_pair_file': '/green/tile_pair_file.txt'
                },
                f)
    elif job_queue == 'Generate MIPMaps':
        with open(args.output_json, 'w') as f:
            json.dump(
                {
                    'output_dir': '/path/to/mock/output/dir'
                },
                f)
    elif job_queue == 'Apply MIPMaps':
        with open(args.output_json, 'w') as f:
            json.dump(
                {
                    'output_stack': 'mock_output_stack',
                    'missing_tilespecs_zs': [1, 2, 3, 4, 5, 6]
                },
                f)
    elif job_queue == '2D Montage Point Match':
        with open(args.output_json, 'w') as f:
            json.dump(
                {
                    'pairCount': 42
                },
                f)
    elif job_queue == 'Detect Defects':
        with open(args.input_json, 'r') as f:
            z_index = json.load(f)['minZ']
        with open(args.output_json, 'w') as f:
            json.dump(
                {
                    'qc_passed_sections': [ z_index ],
                    'gap_sections': [],
                    'seam_sections': [],
                    'hole_sections': []
                },
                f)
        defect_detection_output = os.path.join(
            os.path.dirname(args.output_json),
            'defect_detection_output.json'
        )
        with open(defect_detection_output, 'w') as f:
            json.dump(
                {
                    'this': 'that'
                },
                f)
    elif job_queue == 'Create Rough Tile Pairs':
        with open(args.output_json, 'w') as f:
            json.dump(
                {
                    'tile_pair_file': '/path/to/mock'
                },
                f)
    elif job_queue == 'EM Rough Point Match':
        with open(args.output_json, 'w') as f:
            json.dump(
                {
                    'pairCount': 1234
                },
                f)
    else:
        print("copying %s to %s" % (args.input_json,
                                    args.output_json))

        shutil.copy(args.input_json,
                    args.output_json)


    print("done")

