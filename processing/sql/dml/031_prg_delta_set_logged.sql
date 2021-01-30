create index delta_simc_new on prg.delta_new using hash (teryt_simc);
alter table prg.delta_new set logged;
