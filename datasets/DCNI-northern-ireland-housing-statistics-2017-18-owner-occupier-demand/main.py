# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from gssutils import *

next_table = pd.DataFrame()

# +
# %%capture

# %run "T5.1.py"
next_table = pd.concat([next_table, new_table])
# %run "T5.2.py"
next_table = pd.concat([next_table, new_table])
# %run "T5.3.py"
next_table = pd.concat([next_table, new_table])
# %run "T5.4.py"
next_table = pd.concat([next_table, new_table])
# %run "T5.5.py"
next_table = pd.concat([next_table, new_table])
# %run "T5.6.py"
next_table = pd.concat([next_table, new_table])
# %run "T5.7.py"
next_table = pd.concat([next_table, new_table])
# %run "T5.8.py"
next_table = pd.concat([next_table, new_table])
# %run "T5.9.py"
next_table = pd.concat([next_table, new_table])
# %run "T5.10.py"
next_table = pd.concat([next_table, new_table])

# +
# from pathlib import Path
# out = Path('out')
# out.mkdir(exist_ok=True)
# next_table.drop_duplicates().to_csv(out / 'observations.csv', index = False)

# +
# scraper.dataset.family = 'affordable-housing'
# with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
#     metadata.write(scraper.generate_trig())

# +
# csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
# csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
