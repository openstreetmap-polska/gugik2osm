import argparse
from datetime import datetime, timezone
import urllib.request
import urllib.error
import shutil
from os import path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', help='File path to the directory where files are to be placed.', nargs=1)
    args = vars(parser.parse_args())

    # Download the file from `url` and save it locally under `file_name`:
    for i in range(2, 33, 2):
        woj = str(i).rjust(2, '0')
        dom = 'http://opendata.geoportal.gov.pl/prg/adresy/'
        fn = '{0}_Punkty_Adresowe.zip'.format(woj)
        url = dom + fn
        print(datetime.now(timezone.utc).astimezone().isoformat(), '- downloading:', fn, 'from:', url)
        try:
            with urllib.request.urlopen(url) as response, open(path.join(args['output_dir'][0], fn), 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        except urllib.error.HTTPError as e:
            print(datetime.now(timezone.utc).astimezone().isoformat(), '- There was a problem downloading:', fn,
                  'from:', url,
                  '- Status code:', e.code, '-', e)
