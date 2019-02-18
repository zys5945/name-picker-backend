import numpy as np
import pandas as pd
import rawloader

def aggregate_datasets(df):
    """
        take df produced by load_datasets
        return [df with year column removed (aggregated), total number of names]
        the order of the df is not gauranteed
    """
    if not np.isscalar(df):
        df = pd.concat([df[key] for key in df], ignore_index=True)

    def aggregate_frequency(x):
        return x['frequency'].sum()

    df = df.groupby(['name', 'sex'])\
        .apply(aggregate_frequency)\
        .reset_index()\
        .rename(columns={0: 'frequency'})

    num_names = df['frequency'].sum()

    return [df, num_names]


def load_and_preprocess():
    year_to_df = rawloader.load_datasets(concat=False)

    aggregated_df, total_num = aggregate_datasets(year_to_df)
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

    return [sex_to_aggregated_df, year_to_sex_to_df, rawloader.get_years()]