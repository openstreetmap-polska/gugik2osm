[out:json][timeout:900];
// area(3600049715) = Polska
area(3600049715)->.searchArea;
(
  way["addr:interpolation"](area.searchArea);
);
out body;
>;
out skel qt;
