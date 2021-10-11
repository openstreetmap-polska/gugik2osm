# gugik2osm
_ENG: Tool that prepares packages for JOSM (OpenStreetMap data editor) for easy imports of data from Polish government registries._

Narzędzie do porównywania i przygotowywania importów uwolnionych danych państwowych do OpenStreetMap (OSM). 

Pełny opis w dziale [FAQ/Pomocy](https://budynki.openstreetmap.org.pl/help.html). Zachęcamy do korzystania i zgłaszania uwag oraz pomysłów.

Mamy nadzieję uczynić z tego pomocne narzędzie dla edytorów, które ułatwi import danych z otwartych danych urzędowych do OSM.

https://budynki.openstreetmap.org.pl

## Narzędzia pomocnicze

Przy okazji tworzenia tej aplikacji napisałem kilka skryptów pomocniczych do importu danych z plików XML (GML) z adresami z PRG czy łączenia się z do API GUS w celu pobrania plików z nazwami gmin, miejscowości, ulic (TERYT).

Poniżej krótki opis, może komuś przydadzą się te skrypty w innym celu.

### Plik:
#### processing/scripts/prg_dl.py
Pobiera spakowane pliki XML (GML) z danymi adresowymi (PRG) z geoportalu.

Użycie (windows):
```
python prg_dl.py --output_dir "D:/temp/"
```

Dostępny parametry:
- --output_dir - ścieżka gdzie chcesz zapisać pliki.
- --only - pobierz tylko plik dla wybranego województwa. Podaj dwucyfrowy kod TERYT.

#### processing/parsers/prg.py
Parsuje pliki XML (GML) z danymi adresowymi (PRG). Może zapisać dane wynikowe do bazy PostgreSQL, SQLite, plików CSV lub wydrukuje w konsoli (stdout). Parsowanie metodą SAX dzięki czemu zużycie pamięci RAM jest bardzo niewielkie (50-100mb).

Użycie (windows):
```
python prg.py --input "D:/ścieżka/do/pliku/02_PunktyAdresowe.zip --writer stdout --limit 5
```

Dostępne parametry:
- --input - ścieżka do pliku do przetworzenia
- --writer - której metody zapisu danych wyjściowych chcemy użyć (postgresql, sqlite, csv, stdout)
- --csv_directory - w przypadku wybrania _writer csv_ ten parametr ustawia ścieżkę (folder) gdzie pliki wyjściowe będą zapisane
- --sqlite_file - w przypadku wybrania _writer sqlite_ ten parametr ustawia ścieżkę do bazy sqlite gdzie będą zapisywane dane 
- --dsn - w przypadku wybrania _writer postgresql_ 
- --prep_tables - jeżeli zapisujemy do bazy danych (postgresql lub sqlite) to ten parametr (wystarczy że sam jest obecny nie trzeba mu nic dodatkowo podawać typu true, 1 etc.) powoduje że najpierw tabele w bazie będą usunięte i odtworzone, przydatne przy ładowaniu pierwszego z serii plików
- --limit - przetwórz tylko tyle wierszy. Przydatne do testowania.

#### processing/scripts/teryt_dl.py
Pobiera spakowane pliki z nazwami gmin, miejscowości, ulic z API rejestru TERYT prowadzonego przez GUS i ładuje je do bazy PostgreSQL.

API GUS dla rejestru TERYT: https://api.stat.gov.pl/Home/TerytApi

Użycie (windows):
```
python teryt_dl.py --api_env test --api_user UzytkownikTestowy --api_password demo1234 --dsn "host=localhost port=5432 dbname=test user=test password=test"
```

Dostępne parametry:
- --api_env - środowisko API (prod, test)
- --api_user - użytkownik do API, którego zakłada nam GUS
- --api_password - hasło do użytkownika API
- --dsn - dane do połączenia się z bazą PostgreSQL (parametr przekazywany do metody connect biblioteki psycopg2, szczegóły: https://www.psycopg.org/docs/module.html#psycopg2.connect )

## Dodawanie warstw opartych na skryptach Overpass API

Jedną z funkcji strony jest pobieranie danych z Overpass API, konwersja ich do formatu GeoJSON i prezentacja na stronie w okienku wyboru warstw.

Warstwy odświeżane są raz na dzień.

Dodawanie nowych warstw wymaga dodania kwerendy w języku Overpassa do folderu: _processing/overpass/_ oraz wpisu w pliku konfiguracyjnym: _web/overpass-layers.json_

Wpis wymaga podania stylu warstwy w formacie Mapbox. Opis w dokumentacji: https://docs.mapbox.com/mapbox-gl-js/style-spec/layers/#type

Kwerendy Overpass nie mogą zawierać elementów obsługiwanych tylko przez stronę overpass-turbo.eu, czyli tych zawartych w znakach __"{{ }}"__.

Przykład kwerendy:

```
[out:json][timeout:250];
// area(3600049715) = Polska
area(3600336075)->.searchArea;
(
  way["addr:interpolation"](area.searchArea);
);
out body;
>;
out skel qt;
```

Przykład konfiguracji:

```json
{
  "sources": [
    {
      "id": "test-olayer",
      "name": "Testowa warstwa Overpass",
      "url": "https://budynki.openstreetmap.org.pl/overpass-layers/test.geojson",
      "layers": [
        {
          "id": "test-olayer-lines",
          "type": "line",
          "source": "test-olayer",
          "paint": {
            "line-color": "orange",
            "line-opacity": 0.8,
            "line-width": 5
          },
          "filter": ["==", "$type", "LineString"]
        }
      ]
    }
  ]
}
```

Nazwa pliku geojson będzie taka sama jak nazwa pliku z kwerendą Overpass. ID warstw i źródeł mogą być dowolne (poza już istniejącymi w pliku map.js), ale lepiej, żeby nawiązywały do tego, co się w nich znajduje. 

Jedno źródło może mieć wiele warstw (np. punkty i poligony albo punkty prezentowane jako kropka plus punkty prezentowane jako napis).

## Lokalne środowisko

Lokalne środowisko deweloperskie można uruchomić w kontenerach Docker. Kontener nie jest w pełni funkcjonalny w porównaniu do środowiska produkcyjnego, ale podstawowe rzeczy poza aktualizacją danych powinny działać.

Bazę danych można odtworzyć z [backupu](https://budynki.openstreetmap.org.pl/dane/dbbackup/).
Można użyć PostgreSQL+PostGIS zainstalowanego bezpośrednio na maszynie lub utworzyć kontener Docker z bazą (co pewnie jest rozwiązaniem prostszym skoro i tak mamy zainstalowanego Dockera, żeby odpalić aplikację).

#### Uruchomienie kontenera z Postgisem:
```
docker run --name "postgis" --shm-size=4g -e MAINTAINANCE_WORK_MEM=512MB -p 25432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASS=1234 -e POSTGRES_DBNAME=gis -d -t kartoza/postgis
```
--name - nadaje nazwę dla kontenera, można wybrać dowolną  
--shm-size=4g - dodatkowy parametr zwiększający ilość miejsca tymczasowego, raczej nie jest niezbędny, ale nie zaszkodzi  
-e MAINTAINANCE_WORK_MEM=512MB - zwiększamy dostępną pamięć dla procesów budujących indeksy itp, nie jest niezbędne, ale może się przydać  
-p 25432:5432 - mapujemy porty, numer po lewej to ten którym się będziemy mogli połączyć do bazy z naszego systemu  
-e POSTGRES_USER=postgres - nazwa domyślnego użytkownika dla bazy PostgreSQL  
-e POSTGRES_PASS=1234 - hasło dla powyższego  
-e POSTGRES_DBNAME=gis - tworzy od razu nową bazę (z odblokowanym rozszerzenim PostGIS)  
-d - uruchamia kontener w tle dzięki czemu będzie można zamknąć okno konsoli bez zatrzymywania bazy  
-t kartoza/postgis - nazwa obrazu do uruchomienia, korzystamy z obrazu od razu skonfigurowanego z bazą PostgreSQL i dodatkiem PostGIS  

#### Przywrócenie niezbędnych tabel:
Najpierw tworzymy schematy „prg” i „teryt”:
```
psql -d gis -h localhost -p 25432 -U postgres -c "create schema prg;"
```
```
psql -d gis -h localhost -p 25432 -U postgres -c "create schema teryt;"
```
Następnie przywracamy kilka wybranych tabel i indeksów do schematów public i prg:
```
pg_restore --jobs 2 --no-owner -n public -d gis -h localhost -p 25432 -U postgres db.bak
```
```
pg_restore --jobs 2 --no-owner -n prg -t delta -I delta_gis -I delta_lokalnyid -I delta_simc -d gis -h localhost -p 25432 -U postgres db.bak
```
```
pg_restore --jobs 2 --no-owner -n teryt -d gis -h localhost -p 25432 -U postgres db.bak
```
Na końcu trzeba podać ścieżkę do pliku, jeżeli nie znajduje się w tym folderze, w którym mamy otworzoną konsole.

#### Przygotowanie pliku .env
Najpierw przygotowujemy plik _.env_ w folderze _conf/_ na podstawie _.env_example_ gdzie podajemy IP bazy PostgreSQL, użytkownika, hasło oraz nazwę bazy danych.

IP podajemy dla kontenera od bazy danych (jeżeli baza była uruchamiana instrukcjami powyżej). Można to sprawdzić komendą: 
```docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgis ```
(gdzie postgis to nazwa kontenera z bazą danych).

Zwróć uwagę, że podajemy port, pod którym postgres jest uruchomiony w kontenerze, ponieważ kontenery rozmawiają ze sobą w jednej sieci wirtualnej, trochę inaczej niż kontener z hostem.

#### Budowa kontenera
Przechodzimy w konsoli do folderu gdzie mamy sklonowane repozytorium (do folderu gdzie jest Dockerfile) i uruchamiamy:
```
docker build -t gugik2osm .
```
-t gugik2osm - oznacza nazwę dla naszego obrazu, można zmienić  
. - oznacza obecną lokalizację  

#### Uruchomienie kontenera
Następnie uruchamiamy kontener (windows):
```
docker run --rm -p 45000:80 `
  --mount type=bind,source=C:/Users/Tomasz/PycharmProjects/gugik2osm/app,target=/opt/gugik2osm/app `
  --mount type=bind,source=C:/Users/Tomasz/PycharmProjects/gugik2osm/web,target=/opt/gugik2osm/web `
  --mount type=bind,source=C:/Users/Tomasz/PycharmProjects/gugik2osm/processing,target=/opt/gugik2osm/git/processing `
  -it gugik2osm
```
--rm - powoduje że po wyłączeniu kontenera jest on automatycznie usuwany  
-p 45000:80 - mapowanie portów, numer po lewej oznacza pod jakim portem będziemy mogli się połączyć do kontenera z "zewnątrz" czyli naszej maszyny  
--mount type=bind,source=C:/Users/Tomasz/PycharmProjects/gugik2osm/app,target=/opt/gugik2osm/app - montuje katalog z naszej maszyny w określonym miejscu w kontenerze, trzeba podawać ścieżki absolutne, zmień lewą część na swoją ścieżkę, tak by prowadziła do folderów app, web i processing w sklonowanym repozytorium  
-it - przeciwieństwo -d, uruchamia kontener "na pierwszym planie", dzięki czemu będziemy mogli wykonywać w nim komendy w razie potrzeby  
gugik2osm - nazwa obrazu, który zbudowaliśmy w poprzednim kroku  

Po uruchomieniu kontenera odpali się terminal bash.

#### Zmiana plików strony/aplikacji
Ostatnią rzeczą, jaką powinniśmy zmienić, jest url dla serwera z kafelkami MVT.
W pliku web/map.js znajdujemy fragment:
```
var updatesLayerURL = "https://budynki.openstreetmap.org.pl/updates.geojson";
var vectorTilesURL = "https://budynki.openstreetmap.org.pl/tiles/{z}/{x}/{y}.pbf";
var overpass_layers_url = "https://budynki.openstreetmap.org.pl/overpass-layers.json";
var downloadable_layers_url = "https://budynki.openstreetmap.org.pl/layers/";
```
i zamieniamy url na:
```
var updatesLayerURL = "http://localhost:45000/updates.geojson";
var vectorTilesURL = "http://localhost:45000/tiles/{z}/{x}/{y}.pbf";
var overpass_layers_url = "http://localhost:45000/overpass-layers.json";
var downloadable_layers_url = "http://localhost:45000/layers/";
```
(port podajemy taki jaki ustawiliśmy w parametrze -p dla kontenera aplikacji).

Wszystkie zmiany dla plików HTML/JS i Python powinny być automatycznie widoczne po odświeżeniu strony (rzeczy typu pliki js mogą wymagać odświeżenia wraz z usunięciem cache: ctrl+f5).

W przeglądarce przejdź do http://localhost:45000 (lub pod innym portem zależnie od tego, co zostało ustawione w komendzie docker run).

#### Uruchamianie testów jednostkowych i integracyjnych
Jeżeli pracujemy w systemie Windows, to możemy użyć pomocniczego skryptu PowerShell: run_local_tests_windows.ps1.
