# pyelection

Presidential election data collector in Python 3.6

## Installation

    pip install pyelection


## Example: 2016 US Presidential

    from pyelection import PyElection
    pye = PyElection(year=2016)


#### By state

    import json
    state = pye.get_state_summary()
    print(json.dumps(state, indent=4, sort_keys=True))


#### By candidate

    # optionally, install pandas for pretty output
    import pandas as pd
    candidates = pye.get_candidate_summary()
    pd.DataFrame(candidates)


## Example: Bulk extraction for multiple years

    import time
    data = {}
    for y in range(1956, 2016, 4):
        data[y] = {}
        data[y]['pye'] = PyElection(year=y)
        data[y]['state'] = data[y]['pye'].get_state_summary()
        data[y]['candidate'] = data[y]['pye'].get_candidate_summary()
        time.sleep(0.1)


#### Note: Current status on the working years:

year|state|candidate
---|---|---
2016|Y|Y
2012|Y|Y
2008|Y|Y
2004|Y|Y
2000|Y|Y
1996|Y|Y
1992|Y|Y
1988|Y|Y
1984|Y|Y
1980|Y|Y
1976|Y|Y
1972|Y|Y
1968|Y|Y
1964|Y|Y
1960|Y|Y
1956|Y|Y
1952|Y|Y
1948|Y|Y
1944|Y|Y
1940|N|Y
1936|N|N
1932|Y|Y
1928|Y|Y
1924|N|N
1920|N|N
1916|N|N
1912|N|N
1908|N|N
1904|N|N
1900|N|N
1896|N|N
1892|N|N
1888|N|N
1884|N|N
1880|N|N
1876|N|N
1872|N|N
1868|N|N
1864|N|N
1860|N|N
1856|N|N
1852|N|N
1848|N|N
1844|N|N
1840|N|N
1836|N|N
1832|N|N
1828|N|N
1824|N|N
1820|N|N
1816|N|N
1812|N|N
1808|N|N
1804|N|N
1800|N|N
1796|N|N
1792|N|N
1789|N|N
