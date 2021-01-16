import argparse
import json
from os import walk, path
import logging

import osm2geojson
import requests

DEFAULT_OVERPASS_SERVER = 'https://overpass.kumi.systems/api/interpreter'


def main(input_filepath: str, output_filepath: str, overpass_server: str = DEFAULT_OVERPASS_SERVER) -> None:
    print('Opening query:', input_filepath)
    with open(input_filepath, 'r', encoding='utf-8') as f:
        query = f.read()

    response = None
    try:
        response = requests.post(overpass_server, data={'data': query})
    except:
        logging.error('Error for query:', input_filepath)

    if response:
        if response.ok:
            data = response.json()
            geojson = osm2geojson.json2geojson(data, filter_used_refs=False, log_level='INFO')
            print('Saving file:', output_filepath)
            with open(output_filepath, 'w', encoding='utf-8') as o:
                json.dump(geojson, o)
        else:
            print('Request was not successful.')
            print(response.status_code)
            print(response.text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file', help='Path to file with Overpass query.', nargs='?')
    parser.add_argument('--input-dir', help='Path to directory with Overpass queries.', nargs='?')
    parser.add_argument('--output-file', help='Path for output GeoJSON file.', nargs='?')
    parser.add_argument('--output-dir', help='Path to directory for output GeoJSON files.', nargs='?')
    parser.add_argument('--skip-existing', help='Skip queries that already have GeoJSON in output directory.', nargs='?', const=True)
    args = vars(parser.parse_args())

    if args.get('input_file') and args.get('output_file'):
        main(args['input_file'], args['output_file'])
    elif args.get('input_dir') and args.get('output_dir'):
        # get paths of files
        # r=root, d=directories, f = files
        for r, d, f in walk(args['input_dir']):
            for file in f:
                output_path = path.join(args['output_dir'], path.basename(file).split('.')[0] + '.geojson')
                if args.get('skip_existing') and path.isfile(output_path):
                    print('Skipping:', file)
                    continue
                else:
                    main(path.join(r, file), output_path)
    else:
        print('Unsupported set of parameters. Sorry.')
