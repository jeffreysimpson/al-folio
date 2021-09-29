# encode: utf-8
"""
Convert your ADS Libraries into the markdown publication pages.
"""

import os 
import requests
import pandas as pd
import numpy as np

free_access_keys = {"10.1093/mnras/stab2012": "https://academic.oup.com/mnras/article/507/1/43/6321839?guestAccessKey=bee13ddf-207b-4889-a894-5dcd9488d637",
                    "10.1093/mnras/stz3105": "https://academic.oup.com/mnras/article/491/3/3374/5613398?guestAccessKey=569ca73d-405e-482f-91f9-278fbf620525",
                    "10.1093/mnras/stz2611": "https://academic.oup.com/mnras/article/490/1/741/5570616?guestAccessKey=fef33d34-993b-427d-ad75-c906329b8014",
                    "10.1093/mnras/sty3042": "https://academic.oup.com/mnras/article/482/4/5302/5173100?guestAccessKey=65582380-8b2d-4ef9-b027-428a4f52e95a",
                    "10.1093/mnras/sty1281": "https://academic.oup.com/mnras/article/478/4/4513/4996802?guestAccessKey=02d5df4d-0a31-47d8-ae4d-5d5d6de9e64c",
                    "10.1093/mnras/stz3479": "https://academic.oup.com/mnras/article/492/1/1370/5681406?guestAccessKey=1b2999f1-5e8c-44ee-9a29-6744ee9385b7"}

def get_config():
    """
    Load ADS developer key from file
    :return: str
    """
#     token = os.getenv('ADS_TOKEN')
    try:
        with open(os.path.expanduser('~/.ads/dev_key')) as f:
            token = f.read().strip()
    except IOError:
        print('The script assumes you have your ADS developer token in the'
              'folder: {}'.format())

    return {
        'url': 'https://api.adsabs.harvard.edu/v1/biblib',
        'headers': {
            'Authorization': 'Bearer:{}'.format(token),
            'Content-Type': 'application/json',
        }
    }


def get_bibcodes(library_id):
    """Get the bibcodes for all the papers in the library."""
    start = 0
    rows = 1000
    config = get_config()

    url = f"{config['url']}/libraries/{library_id}"
    r = requests.get(url,
                     params={"start": start,
                             "rows": rows},
                     headers=config["headers"],
    )
    # Get all the documents that are inside the library
    try:
        bibcodes = r.json()["documents"]
    except ValueError:
        raise ValueError(r.text)
    return bibcodes


def get_pub_df(library_id):
    config = get_config()
    bibcodes = get_bibcodes(library_id)

    fields_wants = ["bibcode","title","year","bibstem","author_count","citation_count",
                    "volume","pub","page_range","issue","identifier","author","doi","date","doctype",
                    "abstract", "bibstem"]

    r = requests.post("https://api.adsabs.harvard.edu/v1/search/bigquery",
                      params={"q": "*:*",
                              "fl": ",".join(fields_wants),
                              "rows": 2000},
                      headers={'Authorization': config['headers']['Authorization'],
                               'Content-Type': 'big-query/csv'},
                      data="bibcode\n" + "\n".join(bibcodes))
    doc_dict = r.json()['response']['docs']

    pub_df = pd.DataFrame(doc_dict)
    pub_df.fillna(value=" ", inplace=True)
    return pub_df

def reorder(a):
    a = a.replace("Galah", "GALAH")
    if "," not in a:
        return a
    return a #" ".join([a.split(", ")[1],a.split(", ")[0]])

def get_arxiv_str(pub):
    arXiv_id = [i for i in pub['identifier'] if i.startswith("arXiv:")]
    if len(arXiv_id) == 0:
        return None
    return f"{arXiv_id[0]}"

def fix_title(title):
    things_to_fix = [[r"${S}^5$", "S<sup>5</sup>"]]
    for thing_to_fix in things_to_fix:
        title = title.replace(thing_to_fix[0], thing_to_fix[1])
    return title

def write_bibtex(bibtex_file, pub_df):
    with open(bibtex_file, 'w') as bibfile:
        for *_, publication in pub_df.sort_values(['date', 'bibcode'], ascending=[False, False]).iterrows():
            if publication.doctype in ignore_doctype:
                continue
            bibfile.write(f"@{publication.doctype}")
            bibfile.write("{")
            bibfile.write(f"{publication.bibcode},\n")
            bibfile.write(f"  year={{{publication.year}}},\n")
            bibfile.write(f"  title={{{fix_title(publication.title[0])}}},\n")
            bibfile.write(f"  author={{{' and '.join([reorder(a) for a in publication.author])}}},\n")
            bibfile.write(f"  journal={{{publication.bibstem[0]}}},\n")
            if publication.volume != ' ':
                bibfile.write(f"  volume={{{publication.volume}}},\n")
            if publication.issue != ' ':
                bibfile.write(f"  issue={{{publication.issue}}},\n")
            if publication.page_range != ' ':
                bibfile.write(f"  pages={{{publication.page_range}}},\n")
            if publication.doi != ' ':
                bibfile.write(f"  doi={{{publication.doi[0]}}},\n")
            if get_arxiv_str(publication) is not None:
                bibfile.write(f"  arxiv={{{get_arxiv_str(publication)}}},\n")
            bibfile.write(f"  html={{https://ui.adsabs.harvard.edu/abs/{publication.bibcode}}},\n")
            bibfile.write(f"  abstract={{{publication.abstract}}},\n")
            if publication.bibcode in selected_publications:
                bibfile.write(f"  selected={{true}},\n")
            bibfile.write("}\n\n")

selected_publications = ["2021MNRAS.507...43S",
                         "2021MNRAS.505.5340M",
                         "2020MNRAS.495L.129K",
                         "2020MNRAS.491.2465K",
                         "2020MNRAS.491.3374S",
                         "2020Natur.583..768W",
                         "2019MNRAS.490..741S"]
ignore_doctype = ["catalog", "proposal", "inproceedings", "abstract"]
                    
write_bibtex("assets/bibliography/projects.bib", get_pub_df("8YvxNAmnT1Kf09WBpxQ4Sg"))


pub_df = get_pub_df("XWjvILPkS_qyDvkCLtLOPw")
write_bibtex("_bibliography/papers.bib", pub_df)

h_index = sum(c >= i + 1 for i, c in enumerate(sorted(pub_df.citation_count, reverse=True)))

with open("_pages/publications.md", 'w') as pub_md:
    pub_md.write(f"""---
layout: page
permalink: /publications/
title: publications
description: all of my publications in reversed chronological order. generated by jekyll-scholar.
years: {sorted([int(y) for y in pub_df[~np.isin(pub_df.doctype,ignore_doctype)].year.unique()],reverse=True)}
nav: true
---

<div class="publications">
""")
    pub_md.write(f"""Metrics are obviously problematic, but anyway, I have an h-index of {h_index}.""")
    pub_md.write("""
{% for y in page.years %}
  <h2 class="year">{{y}}</h2>
  {% bibliography -f papers -q @*[year={{y}}]* %}
{% endfor %}

</div>
""")
    