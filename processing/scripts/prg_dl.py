import argparse
from datetime import datetime, timezone
import urllib.request
import urllib.error
import shutil
from os import path


BASE_URL = 'http://opendata.geoportal.gov.pl/prg/adresy/'


def download_file(url: str, file_path: str):
    print(datetime.now(timezone.utc).astimezone().isoformat(), '- downloading:', fn, 'from:', url)
    try:
        with urllib.request.urlopen(url) as response:
            with open(file_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
    except urllib.error.HTTPError as e:
        print(datetime.now(timezone.utc).astimezone().isoformat(), '- There was a problem downloading:', fn,
              'from:', url,
              '- Status code:', e.code, '-', e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', help='File path to the directory where files are to be placed.', nargs=1)
    parser.add_argument('--only', help='Download only this voivodeship\'s file. (provide 2 digit TERYT code)', nargs='?')
    args = vars(parser.parse_args())

    if args.get('only'):
        fn = '{0}_Punkty_Adresowe.zip'.format(args.get('only'))
        url = BASE_URL + fn
        file_path = path.join(args['output_dir'][0], fn)
        download_file(url, file_path)
    else:
        for i in range(2, 33, 2):
            woj = str(i).rjust(2, '0')
            fn = '{0}_Punkty_Adresowe.zip'.format(woj)
            url = BASE_URL + fn
            file_path = path.join(args['output_dir'][0], fn)
            download_file(url, file_path)
