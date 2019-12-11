Zestaw skryptów do utworzenia i replikacji bazy danych OSM

Instrukcja

1. Instalacja zależności:
    - osm2pgsql - aplikacja służąca do importu i aktualizacji danych osm w bazie
    - osmosis - aplikacja służąca do pobierania i processingu plików różnicowych

    `sudo apt install osm2pgsql osmosis`

2. Ustawienie zmiennych środowiskowych

    Kopiujemy plik `cp .env_tmp .env` i ustawiamy w nim parametry dostępu do bazy (host, port, nazwę bazy, użytkownika i hasło)

3. Uruchamiamy db_init.sh, który:
    - Utworzy w klastrze użytkownika z podanym hasłem
    - Utworzy bazę danych zgodnie z parametrami
    - W bazie danych utworzy potrzebne rozszerzenia
    - Pobierze plik ekstraktu danych osm
    - Zaimportuje ekstrakt do bazy
    - usunie plik ekstraktu
    
4. Ustalamy początek replikacji, w tym celu:
    - wchodzimy na adres odnaleziony w pliku konfiguracji osmosis `configuration.txt`, prawdopodobnie będzie to jeden z podkatalogów https://planet.openstreetmap.org/replication/
    - wchodzimy do właściwego folderu i odnajdujemy paczkę z punktu w czasie w którym chcemy rozpocząć replikację (na przykład 2 dni wstecz, bo zaimportowany ekstrakt pochodził z północy - można się dowolnie cofnąć - ponowne zaaplikowanie zmian nie zepsuje bazy danych)
    - dla wybranego punktu w czasie odnajdujemy plik `*.state.txt`
    - w bieżącym folderze (db_scripts) tworzymy plik `state.txt` i kopiujemy do niego zawartość pliku odnalezionego w folderach replikacji na serwerze (poprzedni krok)
    
5. Uruchamiamy skrypt db_update.sh, który:
    - pobierze dane różnicowe z serwerów osm i przetworzy w plik zmian
    - zaimportuje plik zmian do bazy
    
Dalej replikacja może się już odbywać automatycznie - wystarczy dodać wywołanie `db_update.sh` do crontab co zadany okres czasu (np 5 minut).

Jeśli konieczne jest uruchomienie dodatkowych poleceń na bazie danych, które przetworzą dane w bazie po wykonanej aktualizacji polecenia skryptu należy wpisać do pliku postprocessing.sql
