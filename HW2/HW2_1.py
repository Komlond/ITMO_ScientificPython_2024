import requests
import json
import re


def get_uniprot(ids):
    accessions = ','.join(ids)
    endpoint = "https://rest.uniprot.org/uniprotkb/accessions"
    params = {'accessions': accessions}
    response = requests.get(endpoint, params=params)
    return response


def parse_response_uniprot(response):
    data = response.json()
    results = data.get('results', [])
    parsed_data = []
    for result in results:
        accession = result.get('primaryAccession', '')
        species = result.get('organism', {}).get('scientificName', '')
        gene_info = result.get('genes', [])
        sequence_info = result.get('sequence', '')
        parsed_data.append({'accession': accession, 'species': species, 'gene_info': gene_info, 'sequence_info': sequence_info})
    return parsed_data


def get_ensembl(ids):
    server = "http://rest.ensembl.org"
    ext = "/lookup/id"
    headers = {"Content-Type": "application/json"}
    results = []
    for id in ids:
        r = requests.get(server + ext + '/' + id, headers=headers)
        if not r.ok:
            r.raise_for_status()
            continue
        results.append(r.json())
    return results


def parse_response_ensembl(response):
    parsed_data = []
    for result in response:
        parsed_data.append({
            'id': result.get('id', ''),
            'display_name': result.get('display_name', ''),
            'description': result.get('description', ''),
            'biotype': result.get('biotype', ''),
            'organism': result.get('species', {}).get('scientific_name', '')
        })
    return parsed_data


uniprot_regex = re.compile(r'^[OPQ][0-9][A-Z0-9]{3}[0-9]$|^[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$')
ensembl_regex = re.compile(r'^ENS\w{0,}(\d{11})$')


def fetch_and_parse(ids):
    uniprot_match = any(uniprot_regex.match(id) for id in ids)
    ensembl_match = any(ensembl_regex.match(id) for id in ids)

    if uniprot_match:
        database = "UniProt"
    elif ensembl_match:
        database = "ENSEMBL"
    else:
        database = None

    if database == "UniProt":
        get_function = get_uniprot
        parse_function = parse_response_uniprot
    elif database == "ENSEMBL":
        get_function = get_ensembl
        parse_function = parse_response_ensembl
    else:
        raise ValueError("No fitting database found")

    response = get_function(ids)
    parsed_data = parse_function(response)

    return parsed_data


# Example usage:
ids = ["P11473", "Q91XI3"]
parsed_data = fetch_and_parse(ids)
print(parsed_data)
