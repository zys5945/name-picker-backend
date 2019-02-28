from flask import Flask, request, abort, jsonify
import json
import random
import math
import preprocessor
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

sex_to_aggregated_df, year_to_sex_to_df, year_range = preprocessor.load_and_preprocess()

common_percentage = 0.1
rare_percentage = 0.1

"""
    GET

    return

    {
        start: year
        stop: year
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
        type
        sex
        year 
            optional
    }

    return

    {
        name
        description
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

    # determine name
    if name_type == 'random':
        selected_row = df_to_use.iloc[random.randint(0, last_index)]

        name = selected_row['name']
    else:
        if name_type == 'common':
            selected_row = df_to_use.iloc[random.randint(0, math.ceil(0.1 * last_index))]
        elif name_type == 'rare':
            selected_row = df_to_use.iloc[random.randint(math.floor(0.9 * last_index), last_index)]

        name = selected_row['name']

    # get description


    return jsonify({
        'name': name,
        'description': get_name_description(name),
    })


wikiEndpoint = 'https://en.wikipedia.org/wiki/'
wikiURLPatterns = ['<Name>_(given_name)', '<Name>_(name)', '<Name>',]


def get_name_description(name):
    # capitalize first letter
    name = name.lower()
    name = name[0].upper() + name[1:]

    for pattern in wikiURLPatterns:
        response = requests.get(wikiEndpoint + re.sub('<Name>', name, pattern))
        if not response.ok:
            continue

        soup = BeautifulSoup(response.text, features="html.parser")
        main_content = soup.select('.mw-parser-output')[0]

        paragraph_counter = 0
        text = ''

        for child in main_content.children:
            if child.name == 'p':
                text += ' '.join(child.strings)
                paragraph_counter += 1

                if paragraph_counter == 2:
                    break

        # remove all references and things like [ citation needed ]
        text = re.sub('\[.*?\]', '', text)

        # remove last line if the last character is :
        # note paragraphs end with line feed U+000A, thus it is technically the second last character
        if text is not None and len(text) >= 2 and text[-2] == ':': 
            last_period_index = text.rfind('.')
            if last_period_index == -1:
                text = ''
            else:
                text = text[:last_period_index + 1]

        if text != '':
            return text

    return None

from flask_cors import CORS
CORS(app, origins=['http://127.0.0.1:3000'])
app.run()
