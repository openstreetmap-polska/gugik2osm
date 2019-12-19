import datetime
import urllib.request
import urllib.error
import shutil

# Download the file from `url` and save it locally under `file_name`:
for i in range(2, 33, 2):
    woj = str(i).rjust(2, '0')
    dom = 'http://opendata.geoportal.gov.pl/prg/adresy/'
    fn = '{0}_Punkty_Adresowe.zip'.format(woj)
    url = dom + fn
    print(datetime.datetime.now().isoformat(), '- downloading:', fn, 'from:', url)
    try:
        with urllib.request.urlopen(url) as response, open('E:/temp/prg/' + fn, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except urllib.error.HTTPError as e:
        print(datetime.datetime.now().isoformat(), '- There was a problem downloading:', fn, 'from:', url,
              '- Status code:', e.code, '-', e)
