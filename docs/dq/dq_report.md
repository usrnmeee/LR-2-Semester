# DQ Report

| Check                           | Status | Message                                 |
|---------------------------------|--------|-----------------------------------------|
| check_non_empty                 | PASS   | Table has rows                          |
| check_not_null                  | PASS   | No NULL in key columns                  |
| check_unique_key                | PASS   | All rows unique by (country_name, year) |
| check_year_range                | PASS   | All years in [1960, current_year]       |
| check_null_ratio_gdp_diff       | PASS   | NULL ratio acceptable                   |
| check_null_ratio_gdp_growth_pct | PASS   | NULL ratio acceptable                   |
