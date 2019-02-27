from flask import Flask, request, abort, jsonify
import json
import random
import math
import preprocessor

app = Flask(__name__)

sex_to_aggregated_df, year_to_sex_to_df, year_range = preprocessor.load_and_preprocess()

common_percentage = 0.1
rare_percentage = 0.1

"""
    GET

    return

    {
        "start": year
        "stop": year
    }
    years are inclusive
"""
@app.route('/years', methods=['GET'])
def years():
    return jsonify({
        'start': year_range.start,
        'stop': year_range.stop - 1,
    })


sex_options = ['either', 'female', 'male']
type_options = ['random', 'common', 'rare']

"""
    POST

    {
        "type":
        "sex":
        "year": 
            optional
    }

    return

    {
        "name":
    }

"""
@app.route('/name', methods=['POST'])
def name():
    # input processing
    request_json = json.loads(request.data)

    sex = request_json['sex']
    name_type = request_json['type']
    if sex not in sex_options or name_type not in type_options:
        abort(404)

    year = request_json.get('year')
    if year is not None and  year not in year_to_sex_to_df:
        abort(404)
            
    # figure out the appropriate df to use
    df_to_use = None
    if year is None:
        df_to_use = sex_to_aggregated_df[sex]
    else:
        df_to_use = year_to_sex_to_df[year][sex]

    last_index = len(df_to_use) - 1

    # write response
    if name_type == 'random':
        selected_row = df_to_use.iloc[random.randint(0, last_index)]

        return jsonify({
            'name': selected_row['name']
        })
    else:
        if name_type == 'common':
            selected_row = df_to_use.iloc[random.randint(0, math.ceil(0.1 * last_index))]
        elif name_type == 'rare':
            selected_row = df_to_use.iloc[random.randint(math.floor(0.9 * last_index), last_index)]

        return jsonify({
            'name': selected_row['name']
        })
