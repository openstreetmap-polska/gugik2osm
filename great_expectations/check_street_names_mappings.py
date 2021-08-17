import codecs
import sys
from os.path import abspath, join, dirname

import great_expectations as ge
from great_expectations.exceptions import ValidationError


def check_results(results: dict, pad_success: int = 0) -> None:
    if not results['success']:
        print('Check failed')
        print(results)
        sys.exit(1)
    else:
        print((pad_success * ' ') + 'Success.')


expected_columns = [
    'teryt_simc_code',
    'teryt_ulic_code',
    'teryt_street_name',
    'osm_street_name'
]

if len(sys.argv) == 2:
    file_path = sys.argv[1]
else:
    directory = dirname(abspath(__file__))
    file_path = join(directory, '../processing/sql/data/street_names_mappings.csv')

print('Checking if file contains BOM (it should not)...')
with open(file_path, 'rb') as f:
    raw = f.read(4)
    if raw.startswith(codecs.BOM_UTF8):
        print('File contains BOM.')
        sys.exit(1)
print('Success.')

print('Loading file...')
df_ge = ge.read_csv(
    file_path,
    dtype={
        'osm_street_name': 'object',
        'teryt_simc_code': 'object',
        'teryt_street_name': 'object',
        'teryt_ulic_code': 'object'
    },
    encoding='utf-8',
    sep=','
)
print('Done.')

print('Checking if columns are present and in correct order...')
expected_columns_results = df_ge.expect_table_columns_to_match_ordered_list(column_list=expected_columns)
check_results(expected_columns_results)

print('Checking if combinations of teryt simc and ulic codes are unique in the dataset...')
uniqueness_results = df_ge.expect_compound_columns_to_be_unique(column_list=['teryt_simc_code', 'teryt_ulic_code'])
check_results(uniqueness_results)

print('Checking if columns have null values...')
for col in expected_columns:
    print(4 * ' ' + 'Column:', col)
    col_results = df_ge.expect_column_values_to_not_be_null(col)
    check_results(col_results, pad_success=4)

print('Checking if columns with mapped names contain dots (with some exceptions)...')
exceptions = [
    'ps.',
    'C.S.',
    'C.',
    'im.',
]
# C. needs to be in exceptions since C.S. contains two matching dots
print(4 * ' ' + 'exceptions:', exceptions)
pattern_part1 = r'\.(?!(?:'
pattern_part2 = '))'
regex_pattern = pattern_part1 + '|'.join([f'(?<={x.replace(".", r"[.]")})' for x in exceptions]) + pattern_part2
print(4 * ' ' + 'regex pattern (must not match):', regex_pattern)
regex_not_match_results = df_ge.expect_column_values_to_not_match_regex('osm_street_name', regex_pattern)
check_results(regex_not_match_results)

print('All checks done.')
sys.exit(0)
