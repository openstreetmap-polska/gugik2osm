# gugik2osm
Narzędzie do porównywania i przygotowywania importów uwolnionych danych państwowych do OpenStreetMap (OSM). 

## Prace w trakcie

Pełny opis w dziale [FAQ/Pomocy](https://budynki.openstreetmap.org.pl/help.html). Zachęcamy do korzystania i zgłaszania uwag oraz pomysłów.

Mamy nadzieję uczynić z tego pomocne narzędzie dla edytorów, które ułatwi import danych z otwartych danych urzędowych do OSM.

https://budynki.openstreetmap.org.pl

## Lokalne środowisko

Lokalne środowisko deweloperskie można uruchomić w kontenerach Docker. Kontener nie jest w pełni funkcjonalny w porównaniu do środowiska produkcyjnego, ale podstawowe rzeczy poza aktualizacją danych powinny działać.

Bazę danych można odtworzyć z [backupu](https://budynki.openstreetmap.org.pl/dane/dbbackup/).
Można użyć PostgreSQL+PostGIS zainstalowanego bezpośrednio na maszynie lub utworzyć kontener Docker z bazą (co pewnie jest rozwiązaniem prostszym skoro i tak mamy zainstalowanego Dockera żeby odpalić aplikację).

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
Najpierw tworzymy schemat "prg":
```
psql -d gis -h localhost -p 25432 -U postgres -c "create schema prg;"
```
Następnie przywracamy kilka wybranych tabel i indeksów do schematów public i prg:
```
pg_restore --jobs 2 --no-owner -n public -t tiles -t expired_tiles -t prng -t process_locks  -I tiles_zxy_pk -I expired_tiles_pk -I idx_tiles_bbox -I process_locks_pkey -I idx_prng_geom -I idx_prng_count -d gis -h localhost -p 25432 -U postgres db.bak
```
```
pg_restore --jobs 2 --no-owner -n prg -t delta -t lod1_buildings -I delta_gis -I delta_lokalnyid -I delta_simc -I lod1_buildings_geom_idx -I lod1_buildings_pkey -d gis -h localhost -p 25432 -U postgres db.bak
```
Na końcu trzeba podać ścieżkę do pliku jeżeli nie znajduje się w tym folderze w którym mamy otworzoną konsole.

#### Budowa i uruchomienie kontenera
Przechodzimy w konsoli do folderu gdzie mamy sklonowane repozytorium (do folderu gdzie jest Dockerfile) i uruchamiamy:
```
docker build -t gugik2osm .
```
-t gugik2osm - oznacza nazwę dla naszego obrazu, można zmienić  
. - oznacza obecną lokalizację  

Następnie uruchamiamy kontener:
```
docker run --rm -p 45000:80 --mount type=bind,source=C:/Users/Tomasz/PycharmProjects/gugik2osm/app,target=/opt/gugik2osm/app --mount type=bind,source=C:/Users/Tomasz/PycharmProjects/gugik2osm/web,target=/opt/gugik2osm/web -e dsn="host=172.17.0.2 port=5432 user=postgres password=1234 dbname=gis" -it gugik2osm
```
--rm - powoduje że po wyłączeniu kontenera jest on automatycznie usuwany  
-p 45000:80 - mapowanie portów, numer po lewej oznacza pod jakim portem będziemy mogli się połączyć do kontenera z "zewnątrz" czyli naszej maszyny  
--mount type=bind,source=C:/Users/Tomasz/PycharmProjects/gugik2osm/app,target=/opt/gugik2osm/app - montuje katalog z naszej maszyny w określonym miejscu w kontenerze, trzeba podawać ścieżki absolutne, zmień lewą część na swoją ścieżkę tak by prowadziła do folderów app i web w sklonowanym repozytorium  
--mount type=bind,source=C:/Users/Tomasz/PycharmProjects/gugik2osm/web,target=/opt/gugik2osm/web - j.w.  
-e dsn="host=172.17.0.2 port=5432 user=postgres password=1234 dbname=gis" - dodaj parametr z danymi do połączenia do bazy danych, ip podajemy dla kontenera od bazy danych (jeżeli baza była uruchamiana instrukcjami powyżej). Można to sprawdzić komendą: 
```docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgis ``` (gdzie postgis to nazwa kontenera z bazą danych)  
-it - przeciwieństwo -d, uruchamia kontener "na pierwszym planie", dzięki czemu będziemy mogli wykonywać w nim komendy w razie potrzeby  
gugik2osm - nazwa obrazu który zbudowaliśmy w poprzednim kroku  

Po uruchomieniu kontenera odpali się terminal bash.

#### Zmiana plików strony/aplikacji
Ostatnią rzeczą jaką powinniśmy zmienić jest url dla serwera z kafelkami MVT.
W pliku web/map.js znajdujemy fragment:
```
"mvt-tiles": {
    "type": "vector",
    "tiles": [
        "https://budynki.openstreetmap.org.pl/tiles/{z}/{x}/{y}.pbf"
    ]
}
```
i zamieniamy url na:
```
"http://localhost:45000/tiles/{z}/{x}/{y}.pbf"
```
(port podajemy taki jaki ustawiliśmy w parametrze -p dla kontenera aplikacji).

Wszystkie zmiany dla plików HTML/JS i Python powinny być automatycznie widoczne po odśiweżeniu strony (rzeczy typu pliki js mogą wymagać odświeżenia wraz z usunięciem cache: ctrl+f5).
