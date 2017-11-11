import json
from datetime import datetime
from warnings import warn

import pandas as pd
import requests
try:
    from tqdm import tqdm
except ImportError:
    from va_efficiency.constants import tqdm

from va_efficiency.constants import COUNTS, OFFICE_IDS, EARLIEST, LATEST, MAX_RESULTS, URL_BASE


def is_election_year(year, office):
    if office == 'va_senator':
        return (year - 2015) % 4 == 0
    elif office == 'va_delegate':
        return (year - 2017) % 2 == 0


def chunk_queries(office, year_from=EARLIEST, year_to=LATEST):
    queries = [{'year_from': year_from}]
    expected_responses = 0
    for year in range(year_from, year_to+1):
        if is_election_year(year, office):  # odd-year elections
            expected_responses += COUNTS[office]
        if expected_responses > MAX_RESULTS:
            queries[-1]['year_to'] = year - 1
            queries.append({'year_from': year})
            expected_responses = 0

    queries[-1]['year_to'] = year_to
    return queries


def get_response(office, year_from, year_to, session=None):
    query = URL_BASE.format(office_id=OFFICE_IDS[office], year_from=year_from, year_to=year_to)
    session = session or requests

    response = session.get(query)
    response.raise_for_status()
    parsed_response = response.json()
    assert all(len(item) == 0 for item in parsed_response['errors'].values()), 'Response had errors:\n{}'.format(
        json.dumps(parsed_response['errors'], indent=2, sort_keys=True)
    )

    rows = dict()
    for district_election in parsed_response['output']:
        year = datetime.strptime(district_election['Election']['date'], '%Y-%m-%d').year
        try:
            district = int(district_election['District']['name'])
        except ValueError as e:
            if "'5-6-7'" in str(e):
                warn("Found district with name '5-6-7' ({} {}): skipping".format(office, year))
                continue
            else:
                raise e
        r_votes = 0
        d_votes = 0
        for candidate in district_election['Candidate']:
            candidate_to_election = candidate['CandidateToElection']
            n_votes = int(candidate_to_election['n_votes'])
            if candidate_to_election['party'] == 'Republican':
                r_votes += n_votes
            elif candidate_to_election['party'] == 'Democratic':
                d_votes += n_votes

        if r_votes * d_votes == 0:
            continue

        term = int(year / 10) * 10

        rows[(term, year, district)] = {
            'r_votes': r_votes,
            'd_votes': d_votes,
        }

    return rows


def get_data_for_office(office, year_from=EARLIEST, year_to=LATEST, session=None):
    session = session or requests.Session()
    rows = dict()
    for chunk in tqdm(chunk_queries(office, year_from, year_to)):
        rows.update(get_response(office, chunk['year_from'], chunk['year_to'], session))

    df = pd.DataFrame.from_dict(rows, orient='index')
    # total votes, winner, threshold, r_wasted, d_wasted
    df['r_win'] = df['r_votes'] > df['d_votes']
    df['total_votes'] = df['r_votes'] + df['d_votes']
    df['r_ppn'] = df['r_votes'] / df['total_votes']
    df['d_ppn'] = df['d_votes'] / df['total_votes']
    df['threshold'] = ((df['total_votes'] + 1) / 2).astype(int)
    df['r_wasted'] = df['r_win'] * (df['r_votes'] - df['threshold']) + (~df['r_win']) * df['r_votes']
    df['d_wasted'] = (~df['r_win']) * (df['d_votes'] - df['threshold']) + df['r_win'] * df['d_votes']

    return df
