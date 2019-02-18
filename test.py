import requests
import random


host = 'http://localhost:8080/'


def get_years():
    return requests.get(host + 'years')


def get_name(request_type, sex, year):
    request_data = {
        'type': request_type,
        'sex': sex,
    }

    if year is not None:
        request_data['year'] = year

    return requests.post(host + 'name', json=request_data)

def test_year():
    assert get_years().status_code == 200


request_types = ('random', 'rare', 'common')
sexes = ('male', 'female', 'either')
year_range = (1880, 2017) # note can be None

def test_name(N):
    for i in range(N):
        request_type = random.choice(request_types)
        sex = random.choice(sexes)
        year = None if random.randint(0, 1) == 0 else random.randint(*year_range)
        r = get_name(request_type, sex, year)

        try:
            assert r.status_code == 200
            assert r.json().get('name') is not None
        except:
            print(request_type, '\n', sex, '\n', year, '\n')
            raise


if __name__ == '__main__':
    test_year()
    test_name(10000)