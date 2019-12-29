-- https://dba.stackexchange.com/questions/175368/compare-words-in-a-string-without-considering-their-positions
create or replace function strings_equivalent(a text, b text)
returns boolean as $$
select
  case
    when length(a) >= length(b) then (
      select count( exa1 ) from (
        select unnest( string_to_array( a, ' ' ) )
        except all
        select unnest( string_to_array( b, ' ' ) ) ) exa1
      ) = 0
    when length(a) < length(b) then (
      select count( exa2 ) from (
        select unnest( string_to_array( b, ' ' ) )
        except all
        select unnest( string_to_array( a, ' ' ) ) ) exa2
      ) = 0
    else false
  end
$$ language sql immutable;