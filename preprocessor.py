import numpy as np
import pandas as pd
import rawloader
import ujson

def aggregate_datasets(arg):
    """
        take output produced by load_datasets
        return [df with year column removed (freqency aggregated by (name, sex)), total number of names]
        the order of the df is not gauranteed
    """
    # produce aggregated df by (name, sex)
    if not np.isscalar(arg):
        df = pd.concat([arg[key] for key in arg], ignore_index=True)

    aggregated_df = df.groupby(['name', 'sex'])\
        .apply(lambda x: x['frequency'].sum())\
        .reset_index()\
        .rename(columns={0: 'frequency'})

    num_names = aggregated_df['frequency'].sum()

    # produce name to json, where the json is the serialized object of year to frequency
    def agg(df):
        return df['frequency'].sum()
    df_with_year = rawloader.load_datasets()
    name_to_year_to_frequency = df_with_year.groupby(['name', 'year']).apply(agg)

    name_to_json = {}
    for name in name_to_year_to_frequency.index.get_level_values(0):
        name_to_json[name] = ujson.dumps(name_to_year_to_frequency[name].to_dict())

    return [aggregated_df, name_to_json, num_names]


def load_and_preprocess():
    year_to_df = rawloader.load_datasets(concat=False)

    aggregated_df, name_to_json, total_num = aggregate_datasets(year_to_df)
    aggregated_male_df = aggregated_df[aggregated_df['sex'] == 'M']
    aggregated_female_df = aggregated_df[aggregated_df['sex'] == 'F']

    year_to_sex_to_df = {}

    for year in year_to_df:
        df = year_to_df[year]
        year_to_sex_to_df[year] = {
            'male': df[df['sex'] == 'M'],
            'female': df[df['sex'] == 'F'],
            'either': df,
        }

    sex_to_aggregated_df = {
        'male': aggregated_male_df,
        'female': aggregated_female_df,
        'either': aggregated_df,
    }

    return [sex_to_aggregated_df, year_to_sex_to_df, name_to_json,rawloader.get_years()]