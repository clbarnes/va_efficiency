import os


def tqdm(iterable):
    """Dummy tqdm for simple use case"""
    return iterable


PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

EARLIEST = 1947  # US Rep data goes earlier, but VA data starts in '47
LATEST = 2016  # 2017 election isn't finalised yet

PARTIES = {'Democratic', 'Republican'}  # ignore others for simplicity

MAX_RESULTS = 400  # the website truncates results if there are more than 600; this allows for special elections etc.

URL_BASE = 'http://historical.elections.virginia.gov/elections/search/year_from:{year_from}' \
           '/year_to:{year_to}/office_id:{office_id}/stage:General.json'

GAP_LIMIT = 8  # McGhee + Stephanopoulos' recommended constitutional limit for % efficiency gap

COUNTS = {  # max number of seats
    'va_delegate': 100,
    'va_senator': 40,
    'us_representative': 12
}
OFFICE_IDS = {
    'va_delegate': 8,
    'va_senator': 9,
    'us_representative': 5
}
X_JITTER = {
    'us_representative': -0.5,
    'va_delegate': 0,
    'va_senator': 0.5
}
LABELS = {
    'us_representative': 'U.S. Rep.',
    'va_delegate': 'VA Del.',
    'va_senator': 'VA Sen.'
}
