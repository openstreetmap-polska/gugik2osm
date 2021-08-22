create table if not exists teryt.cecha_mapping (
    cecha text primary key,
    m text not null
);

-- m column is going to be either text mapping or empty string for further ease of processing
insert into teryt.cecha_mapping values
('ul.', ''),
('al.', 'Aleja'),
('pl.', 'Plac'),
('skwer', 'Skwer'),
('bulw.', 'Bulwar'),
('rondo', 'Rondo'),
('park', 'Park'),
('rynek', 'Rynek'),
('szosa', ''),
('droga', ''),
('os.', 'Osiedle'),
('wyspa', 'Wyspa'),
('wyb.', 'Wybrzeże'),
('inne', '')
on conflict do nothing
;
