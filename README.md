# pyelection

Presidential election data collector in Python

## Installation

    pip install pyelection

## Example: 2016 US Presidential

    from pyelection import PyElection
    pye = PyElection(2016)


#### By state

    import json
    state = pye.get_state_summary()
    json.dumps(state, indent=4, sort_keys=True)


#### By candidate

    import pandas as pd # need to install pandas
    candidates = pye.get_candiate_summary()
    pd.DataFrame(candidates)
