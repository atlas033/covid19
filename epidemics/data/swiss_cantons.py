"""
This file provides access to all relevant data aobut Swiss cantons and COVID-19:
    - list of cantons and their population count
    - connectivity matrix between cantons (number of daily commuters)
    - number of cases per day, for each canton
    - number of foreign infected commuters that resided in switzerland, per day and canton
"""

from epidemics.data import DATA_CACHE_DIR, DATA_DOWNLOADS_DIR, DATA_FILES_DIR
from epidemics.data.cases import get_region_cases
from epidemics.data.population import get_region_population
from epidemics.tools.cache import cache, cache_to_file
from epidemics.tools.io import download_and_save
import epidemics.data.swiss_municipalities as swiss_mun
import numpy as np

import datetime

DAY = datetime.timedelta(days=1)

# https://en.wikipedia.org/wiki/Cantons_of_Switzerland
CANTON_POPULATION = dict(zip(
    'ZH BE LU UR SZ OW NW GL ZG FR SO BS BL SH AR AI SG GR AG TG TI VD VS NE GE JU'.split(),
    [
        1520968,
        1034977,
        409557,
        36433,
        159165,
        37841,
        43223,
        40403,
        126837,
        318714,
        273194,
        200298,
        289527,
        81991,
        55234,
        16145,
        507697,
        198379 ,
        678207,
        276472,
        353343,
        799145,
        343955,
        176850,
        499480,
        73419,
    ]))

CANTON_KEYS_ALPHABETICAL = sorted(CANTON_POPULATION.keys())

def fetch_openzh_covid_data(*, cache_duration=3600):
    """
    Returns a dictionary of lists {canton abbreviation: number of cases per day}.
    """
    url = 'https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/covid19_cases_switzerland_openzh.csv'
    path = DATA_DOWNLOADS_DIR / 'covid19_cases_switzerland_openzh.csv'

    raw = download_and_save(url, path, cache_duration=cache_duration)
    rows = raw.decode('utf8').split()
    cantons = rows[0].split(',')[1:-1]  # Skip the "Date" and "CH" cell.

    data = {canton: [] for canton in cantons}
    for day in rows[1:]:  # Skip the header.
        cells = day.split(',')[1:-1]  # Skip "Date" and "CH".
        assert len(cells) == len(cantons), (len(cells), len(cantons))

        for canton, cell in zip(cantons, cells):
            data[canton].append(float(cell or 'nan'))
    return data



COMMUTE_ADMIN_CH_CSV = DATA_FILES_DIR / 'switzerland_commute_admin_ch.csv'

@cache
@cache_to_file(DATA_CACHE_DIR / 'home_work_people.json',
               dependencies=[COMMUTE_ADMIN_CH_CSV])
def get_Cij_home_work_bfs():
    """
    Returns a dictionary
    {canton1: {canton2: number of commuters between canton1 and canton2, ...}, ...}.
    """
    commute = swiss_mun.get_residence_work_cols12568()

    Cij = {
        c1: {c2: 0 for c2 in CANTON_KEYS_ALPHABETICAL}
        for c1 in CANTON_KEYS_ALPHABETICAL
    }
    for home, work, num_people in zip(
            commute['canton_home'],
            commute['canton_work'],
            commute['num_people']):
        if home != work and work != 'ZZ':
            Cij[work][home] += num_people

    return Cij


def json_to_numpy_matrix(json, order):
    """Returns a json {'A': {'A': ..., ...}, ...} matrix as a numpy matrix.

    Arguments:
        json: A matrix in a JSON dictionary format.
        order: The desired row and column order in the output matrix.
    """
    assert len(order) == len(json), (len(order), len(json))
    out = np.zeros((len(order), len(order)))
    for index1, c1 in enumerate(order):
        for index2, c2 in enumerate(order):
            out[index1][index2] = json[c1][c2]
    return out


def get_Mij_numpy(canton_order):
    """Return the Mij numpy matrix using the data from bfs.admin.ch."""
    # NOTE: This is not the actual migration matrix!
    Cij = get_Cij_numpy(canton_order)
    return Cij + Cij.transpose()


def get_Cij_numpy(canton_order):
    """Return the mij numpy matrix using the data from bfs.admin.ch."""
    return json_to_numpy_matrix(get_Cij_home_work_bfs(), canton_order)


def get_external_Iu(start_date, num_days):
    """Return an estimate of number of undocumented infected foreigns commuting to Switzerland, per canton, per day.

    We use the number of documented infected foreigns to estimate the number of undocumented:
        Iu(t) ~= Ir(t + 1) - Ir(t)

    Returns a dictionary {canton key: [day1, day2, ...]}.

    Sources:
        Number of commuters
        https://www.pxweb.bfs.admin.ch/pxweb/en/px-x-0302010000_108/px-x-0302010000_108/px-x-0302010000_108.px
        Select "Gender - Total", all cantons, "Group of age - Total", "2019Q4".

        Border with Italy partially closed on March 17.
        https://www.swissinfo.ch/eng/covid-19_switzerland-declares-coronavirus-crisis-an--extraordinary--situation/45620148

        Borders with all other neighboring countries partially closed on March 25.
        https://www.swissinfo.ch/eng/coronavirus_switzerland-extends-border-controls-to-all-schengen-states/45642706
    """
    if not isinstance(start_date, datetime.date):
        start_date = datetime.date.fromisoformat(start_date)

    # Foreign region keys.
    FR = 'france'
    GE = 'germany'
    AU = 'austria'
    IT = 'italy'

    # We approximate the inflow graph by considering only one external country
    # per canton. To split an inflow to multiple foreign countries, just add
    # multiple tuples per canton.
    DATA = [
        ('ZH', GE, 10404.7),
        ('BE', FR, 3514.7),
        ('LU', GE, 613.8),
        ('UR', IT, 46.0),
        ('SZ', AU, 372.9),
        ('OW', IT, 117.6),
        ('NW', IT, 88.2),
        ('GL', AU, 61.4),
        ('ZG', GE, 996.2),
        ('FR', FR, 1027.9),
        ('SO', FR, 2151.6),
        ('BS', GE, 33932.4),
        ('BL', GE, 22318.4),
        ('SH', GE, 4932.3),
        ('AR', AU, 400.4),
        ('AI', AU, 99.7),
        ('SG', AU, 9199.6),
        ('GR', IT, 6998.4),   # Partially incorrect.
        ('AG', GE, 13915.3),
        ('TG', GE, 5586.6),
        ('TI', IT, 67878.4),
        ('VD', FR, 32425.2),
        ('VS', FR, 3079.1),
        ('NE', FR, 12944.3),
        ('GE', FR, 87103.8),
        ('JU', FR, 8640.8),
    ]
    A = set(c for c, ext, num in DATA)
    B = set(CANTON_KEYS_ALPHABETICAL)
    assert A == B, f"You forgot some cantons:\n{A - B}\n{B - A}"

    BORDERS_CLOSING_DATE = {
        FR: '2020-03-25',
        GE: '2020-03-25',
        AU: '2020-03-25',
        IT: '2020-03-17',
    }
    BORDERS_CLOSING_DATE = {key: datetime.date.fromisoformat(date) for key, date in BORDERS_CLOSING_DATE.items()}

    # Also, we use data on whole countries as an approximation to the data of
    # regions at the Swiss border. To fix this, instead of using FR/GE/AU/IT
    # above, add their regions (counties or whatever) and extend
    # `get_region_cases` to include this regions.
    COUNTRY_IR = {country: get_region_cases(country) for country in BORDERS_CLOSING_DATE.keys()}
    COUNTRY_POPULATION = {country: get_region_population(country) for country in BORDERS_CLOSING_DATE.keys()}

    result = {c: [0] * num_days for c in CANTON_KEYS_ALPHABETICAL}
    for canton, country, inflow in DATA:
        result_old = result[canton][:]
        for day in range(num_days):
            date = start_date + day * DAY

            if date < BORDERS_CLOSING_DATE[country]:
                intervention_factor = 1.0
            else:
                # TODO: This is probably not correct. Did France and other
                # countries shut down the border from Switzerland to them, or
                # did only Switzerland close the borders? What about Swiss
                # residents working abroad?
                intervention_factor = 0.0

            # The estimated number of infected people that arrived from
            # `country` to `canton` at the date `date`.
            country_Ir = COUNTRY_IR[country].get_confirmed_at_date
            iu_estimate = max(0, country_Ir(date + DAY) - country_Ir(date))
            inflow = iu_estimate / COUNTRY_POPULATION[country] * intervention_factor
            # print(country_Ir(date), iu_estimate, COUNTRY_POPULATION[country], intervention_factor, inflow)
            result[canton][day] += inflow
        # print(country, canton, " ".join(str(int(1e6 * (x - y))) for x, y in zip(result[canton], result_old)))

    return result
