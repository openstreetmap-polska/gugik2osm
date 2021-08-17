import sys

import great_expectations as ge
from great_expectations.exceptions import ValidationError


def check_results(results: dict) -> None:
    if not results['success']:
        print('Check failed')
        print(results)
        sys.exit(1)
    else:
        print('Success')


expected_columns = [
    'teryt_simc_code',
    'teryt_ulic_code',
    'teryt_street_name',
    'osm_street_name'
]

print('Loading file...')
df_ge = ge.read_csv(
    '../processing/sql/data/street_names_mappings.csv',
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

checks = [

]

print('Checking if columns are present and in correct order...')
expected_columns_results = df_ge.expect_table_columns_to_match_ordered_list(column_list=expected_columns)
check_results(expected_columns_results)

print('Checking if combinations of teryt simc and ulic codes are unique in the dataset...')
uniqueness_results = df_ge.expect_compound_columns_to_be_unique(column_list=['teryt_simc_code', 'teryt_ulic_code'])
check_results(uniqueness_results)

print('All checks done.')
sys.exit(0)
