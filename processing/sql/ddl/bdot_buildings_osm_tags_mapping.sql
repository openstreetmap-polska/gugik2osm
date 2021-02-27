drop table if exists bdot.buildings_categories_mappings;
create table if not exists bdot.buildings_categories_mappings (
  kategoria_bdot text not null,
  funkcja_ogolna_budynku text not null,
  funkcja_szczegolowa_budynku text not null,
  building text,
  amenity text,
  man_made text,
  leisure text,
  historic text,
  tourism text,
  constraint buildings_categories_mappings_pk primary key (kategoria_bdot, funkcja_ogolna_budynku, funkcja_szczegolowa_budynku)
);
