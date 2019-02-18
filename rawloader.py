# project walkthrough https://engmrk.com/module8-data-science-project-1/
# project data https://catalog.data.gov/dataset/baby-names-from-social-security-card-applications-national-level-data
# data in format name sex frequency, each year stored separately in yob<year>.txt

import numpy as np
import pandas as pd
import pathlib


def load_csv(filenames, raise_on_error=True, header='infer', names=None):
    """
    :param filenames: sequence of file names
    :param header: passed directly to read_csv
    :return: (list of (filename, dataframe) pairs, list of file names that are missing / not a regular file)
            if raise_on_error=False, otherwise just the dfs_and_names pair
    """

    if np.isscalar(filenames):
        filenames = [filenames]

    dfs_and_names = []
    errors = []

    for f in filenames:
        path = pathlib.Path(f)

        if not path.is_file():
            errors.append(path)
            continue

        dfs_and_names.append((
            pd.read_csv(f, header=header, names=names),
            f
        ))

    if raise_on_error:
        if len(errors) != 0:
            raise ValueError('unable to open files {0}'.format(errors))
        else:
            return dfs_and_names
    else:
        return dfs_and_names, errors

def get_filenames():
    for year in get_years():
        yield get_filename_from_year(year)

def get_years():
    return range(1880, 2018)

def get_year_from_filename(filename):
    return int(filename[9:13])


def get_filename_from_year(year):
    return 'names/yob{0}.txt'.format(year)

def load_datasets(concat=True):
    """
        if concat then return a df with columns year, name, sex, frequency
        otherwise return a dictionary with year: df
    """

    dfs_and_names = load_csv(get_filenames(), header=None, names=['name', 'sex', 'frequency'])

    if concat:
        for pair in dfs_and_names:
            df = pair[0]
            filename = pair[1]

            df['year'] = get_year_from_filename(filename)

        return pd.concat((pair[0] for pair in dfs_and_names), ignore_index=True)
    else:
        return {get_year_from_filename(pair[1]): pair[0] for pair in dfs_and_names}