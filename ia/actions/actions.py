from typing import Optional, List
import spacy
import re
from functools import reduce

def get_country_from_message(user_message: str) -> Optional[str]:
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(user_message)
            for ent in doc.ents:
                if ent.label_ == "GPE":
                    return ent.text
            return None

def get_years_from_message(user_message: str) -> List[int]:
    return [int(year) for year in re.findall(r'\b\d{4}\b', user_message)]

def filter_data(data, country=None, year_start=None, year_end=None, year=None):
    conditions = []
    if country:
        conditions.append(data["Country"] == country)
    if year_start:
        conditions.append(data["year"] >= year_start)
    if year_end:
        conditions.append(data["year"] <= year_end)
    if year:
        conditions.append(data["year"] == year)

    if conditions:
        return data[reduce(lambda x, y: x & y, conditions)]
    else:
        return data