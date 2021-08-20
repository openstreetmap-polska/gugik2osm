import argparse
from glob import glob
import os
import re
import requests


STATUS_CONTINUE = 0
STATUS_BREAK_LOOP = 1


def download_file(url: str, file_path: str) -> int:
    # download file from url
    # this method only works for small files
    response = requests.get(url)

    # validate response from the server
    if response.status_code == 404:
        print('No more files to download. Exiting.')
        return STATUS_BREAK_LOOP

    if not response.ok:
        print(f'Error while requesting: {file_path}')
        print(f'Status code: {response.status_code}')
        print(f'Response text {response.text}')
        print('Exiting.')
        return STATUS_BREAK_LOOP

    # save file
    dir_path = os.path.dirname(file_path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    with open(file_path, 'wb') as f:
        print(f'Saving file: {file_path}')
        f.write(response.content)
    return STATUS_CONTINUE


def download_changesets(
        output_dir: str,
        starting_point: str = '004/260/811',  # start of 2021
        url: str = 'https://planet.osm.org/replication/changesets/',
        limit: int = None,
        overwrite_existing: bool = False,
        auto_starting_point: bool = False
) -> None:

    if not os.path.isdir(output_dir):
        raise ValueError(f'Parameter output_dir: "{output_dir}" has invalid value.')

    if auto_starting_point:
        files = glob(os.path.join(output_dir, '**/*.osm.gz'), recursive=True)
        if len(files) == 0:
            raise ValueError(
                'Didn\'t find any existing files. Parameter "auto_starting_point" cannot be set to "True".')
        last_file = sorted(files)[-1]
        starting_point = re.search(
            r'[\\/]{1,2}\d{3}[\\/]{1,2}\d{3}[\\/]{1,2}\d{3}\.osm\.gz',
            last_file,
            re.IGNORECASE
        ).group(0).replace('\\', '/')[:-7]
        print(f'Starting from: {starting_point}')

    # set initial values
    counter = 0
    parts = starting_point.strip('/').split('/')
    p1 = parts[0]
    p2 = parts[1] if len(parts) > 1 else '0'
    p3 = parts[2] if len(parts) > 2 else '0'
    num1, num2, num3 = int(p1), int(p2), int(p3)

    while True:
        # generate full url and request file
        suffix = '/'.join([
            str(num1).zfill(3),
            str(num2).zfill(3),
            str(num3).zfill(3) + '.osm.gz'
        ])
        full_url = os.path.join(url, suffix)
        full_path = os.path.abspath(os.path.join(output_dir, suffix))

        if not overwrite_existing and os.path.isfile(full_path):
            print(f'File: {full_path} already exists. Skipping.')
        else:
            status = download_file(full_url, full_path)
            if status == STATUS_BREAK_LOOP:
                break

        # increment numbers
        if num3 == 999 and num2 == 999:
            num1 += 1
            num2 = 0
            num3 = 0
        elif num3 == 999:
            num2 += 1
            num3 = 0
        else:
            num3 += 1
        counter += 1

        if limit and counter == limit:
            print(f'Limit of {limit} reached. Exiting.')
            break
    print(f'Processed: {counter} files.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--changesets-dir', help='Path to the directory where files are to be placed.', nargs=1)
    parser.add_argument('--limit', help='Limit download to N elements.', nargs='?', type=int)
    parser.add_argument(
        '--starting-point',
        help='Starting point for download (changeset file name). Can be one of: ddd, ddd/ddd, ddd/ddd/ddd where d is a digit.',
        nargs='?'
    )
    parser.add_argument(
        '--auto-starting-point',
        help='Automatically find starting point based off of files already present in the directory. Overwrites starting-point arg.',
        nargs='?',
        const=True
    )
    parser.add_argument('--overwrite', help='Overwrite existing files.', nargs='?', const=True)
    args = vars(parser.parse_args())

    # starting_point = '004/260/811'  # start of 2021
    # starting_point = '003/742/653'  # start of 2020
    parameters = {
        'starting_point': args.get('starting_point'),
        'output_dir': args.get('changesets_dir')[0],
        'auto_starting_point': True if args.get('auto_starting_point') else False,
    }
    if args.get('limit'):
        parameters['limit'] = args.get('limit')

    download_changesets(**parameters)
