from collections import OrderedDict
import requests
import zipfile
import io
import os
import json

import pandas as pd
from bs4 import BeautifulSoup

BASE_URL = "https://www.psp.cz"


def download_zip_file(url, extract_path, files=None):
    """ Downloads and extracts .zip file from the given URL.

    Args:
        url (str): URL from which data should be downloaded.
        extract_path (str): Path where data will be extracted.
        files (list, optional): 
            List of files to extract from the .zip file.
            All files are extracted if files is None. Defaults to None.
    """

    response = requests.get(url)

    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zip_file:
            if files is not None:
                for file in files:
                    zip_file.extract(file, extract_path)
            else:
                zip_file.extractall(extract_path)

def process_wikidata_files():
    """ Downloads occupations of czech MPs from the wikidata. Doesn't download data
        if JSON already exists.
    """

    json_file = os.path.join(os.getcwd(), "data", "wikidata", "data.json")

    if os.path.exists(json_file):
        print('JSON already exists...')
    else:
        query = '''
            SELECT ?czechParliamentIdLabel ?itemLabel ?birthDate ?occupationLabel WHERE {
                ?item wdt:P31 wd:Q5 .                        # is instance of human  
                ?item wdt:P39 wd:Q19803234 .                 # is MP  

                ?item wdt:P6828 ?czechParliamentId .         # store value of Parlament ID into ?czechParliamentId variable  
                ?item wdt:P106 ?occupation .                 # store occupation into ?occupation variable
                ?item wdt:P569 ?birthDate .

                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],cs". }

                FILTER( ?occupation != wd:Q82955)            # filter occupation "politician" (since every MP is a politican)
            }
        '''
        url = 'https://query.wikidata.org/sparql'

        content = requests.get(url, params = {'format': 'json', 'query': query})
        occupations_json = content.json()

        occupations_list = []
        for occupation_data in occupations_json['results']['bindings']:
            occupations_list.append(OrderedDict({
                label: occupation_data[label]['value'] if label in occupation_data else None
                for label in occupations_json['head']['vars']
            }))

        json_data = {'data': occupations_list}
        with open(json_file, 'w', encoding='utf8') as outfile:
            json.dump(json_data, outfile, ensure_ascii=False)

def process_psp_files():
    """ Downloads .unl files from psp. Doesn't download files
        if all files exist.
    """

    exists = True
    path_to_extract = os.path.join(os.getcwd(), "data", "psp")

    # if at least one file is missing, download all the data again
    files = ['hlasovani.unl', 'organy.unl', 'osoby.unl', 'poslanec.unl']
    for file in files:
        if not os.path.exists(os.path.join(path_to_extract, file)):
            exists = False
            break

    if not exists:

        print(f'Files missing, downloading from {BASE_URL}...')

        # download files dynamically
        response = requests.get(BASE_URL + "/sqw/hp.sqw?k=1300")
        soup = BeautifulSoup(response.content, 'html')

        table_data = soup.find('table').find_all('a', href=True)

        # download mps data
        mps_url = BASE_URL + table_data[0]['href'][2:]
        download_zip_file(mps_url, path_to_extract, files=['organy.unl', 'poslanec.unl', 'osoby.unl'])
        
        # download votings data
        votings_url = BASE_URL + table_data[2]['href'][2:]
        votings_year = votings_url[-10:-6]
        voting_files = [f'hl{votings_year}h1.unl', f'hl{votings_year}h2.unl']
        download_zip_file(votings_url, path_to_extract, files=voting_files)

        # merge h1 and h2 files into one
        with open(os.path.join(path_to_extract, "hlasovani.unl"), 'w') as outfile:
            for fname in voting_files:
                with open(os.path.join(path_to_extract, fname)) as infile:
                    for line in infile:
                        outfile.write(line)

        # remove h1 and h2 files
        for fname in voting_files:
            os.remove(os.path.join(path_to_extract, fname))
    else:
        print("All files exist...")

def load_groups():
    file = os.path.join(os.getcwd(), "data", "psp", "organy.unl")

    groups = pd.read_csv(file, sep='|', encoding='cp1250', header=None, usecols=[i for i in range(10)])
    groups.columns = ['id_organ', 'organ_id_organ', 'id_typ_organu', 'zkratka', 'nazev_organu_cz', 'nazev_organu_en', 'od_organ', 'do_organ', 'priorita', 'cl_organ_base']

    groups = groups[['id_organ', 'zkratka', 'od_organ', 'do_organ']]

    return groups

def load_mps():
    file = os.path.join(os.getcwd(), "data", "psp", "poslanec.unl")

    mps = pd.read_csv(file, sep='|', encoding='cp1250', header=None, usecols=[i for i in range(15)])
    mps.columns = ['id_poslanec', 'id_osoba', 'id_kraj', 'id_kandidatka', 'id_obdobi', 'web', 'ulice', 'obec', 'psc', 'email', 'telefon', 'fax', 'psp_telefon', 'facebook', 'foto']

    mps = mps[['id_poslanec', 'id_osoba', 'id_kandidatka', 'id_obdobi']]

    return mps

def load_persons():
    file = os.path.join(os.getcwd(), "data", "psp", "osoby.unl")

    persons = pd.read_csv(file, sep='|', encoding='cp1250', header=None, usecols=[i for i in range(9)])
    persons.columns = ['id_osoba', 'pred', 'prijmeni', 'jmeno', 'za', 'narozeni', 'pohlavi', 'zmena', 'umrti']

    return persons

def load_votings():
    file = os.path.join(os.getcwd(), "data", "psp", "hlasovani.unl")

    votings = pd.read_csv(file, sep='|', encoding='cp1250', header=None, usecols=[i for i in range(3)])
    votings.columns = ['id_poslanec', 'id_hlasovani', 'vysledek']

    votings = votings[votings['vysledek'].isin(['A','B','N','C'])]
    votings['vysledek'] = votings['vysledek'].replace('N','B')

    votings = votings.pivot(index='id_poslanec', columns='id_hlasovani').fillna('X')

    # one-hot encode data
    votings = pd.get_dummies(votings)

    return votings

def load_occupations():

    json_file = os.path.join(os.getcwd(), "data", "wikidata", "data.json")

    with open(json_file, encoding='utf-8') as json_file:
        data = json.load(json_file)

        occupations = pd.DataFrame(data["data"])
        occupations = occupations[['czechParliamentIdLabel','occupationLabel']].drop_duplicates()
        occupations = occupations[~occupations['occupationLabel'].str.startswith('Q', na=False)]
        occupations = occupations.groupby(['czechParliamentIdLabel']).agg({'occupationLabel': lambda x: x.tolist()}).reset_index()
        occupations['czechParliamentIdLabel'] = occupations['czechParliamentIdLabel'].astype(int)

        occupations.columns = ['id_osoba','povolani']

        return occupations