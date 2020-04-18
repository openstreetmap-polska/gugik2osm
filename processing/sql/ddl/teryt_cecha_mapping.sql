create table if not exists teryt.cecha_mapping (
    cecha text primary key,
    m text not null
);

-- m column is going to be either text mapping or empty string for further ease of processing
insert into teryt.cecha_mapping values
('ul.', ''),
('al.', 'aleja'),
('pl.', 'plac'),
('skwer', 'skwer'),
('bulw.', 'bulwar'),
('rondo', 'rondo'),
('park', 'park'),
('rynek', 'rynek'),
('szosa', ''),
('droga', ''),
('os.', 'osiedle'),
('wyspa', 'wyspa'),
('wyb.', 'wybrzeże'),
('inne', '')
on conflict do nothing
;
