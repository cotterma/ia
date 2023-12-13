from typing import Text, List, Any, Dict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
import spacy
import re

class ActionHDI(Action):
    def name(self) -> Text:
        return "action_hdi"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = pd.read_excel("../data/cleaned_data.xlsx")
        
        intent = tracker.latest_message['intent'].get('name')
        user_message = tracker.latest_message.get("text")

        # Utilisation de spaCy pour extraire le nom du pays
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(user_message)
        country = None
        for ent in doc.ents:
            if ent.label_ == "GPE":
                country = ent.text
                break

        # Utilisation d'expressions régulières pour extraire l'année ou les années de début et de fin
        years = re.findall(r'\b\d{4}\b', user_message)
        if years:
            if len(years) == 1:
                year = int(years[0])
                year_start, year_end = year, year
            elif len(years) == 2:
                year_start = int(years[0])
                year_end = int(years[1])

        if country and year_start and year_end:
            if intent == "inform_hdi":
                # Filtrer les données pour le pays et la période spécifiés
                filtered_data = df[(df["Country"] == country) & (df["year"] >= year_start) & (df["year"] <= year_end)]
                if not filtered_data.empty:
                    if "maximum" in user_message:
                        max_hdi = filtered_data["Human_dev_index"].max()
                        dispatcher.utter_message(f"The maximum HDI for {country} from {year_start} to {year_end} is {max_hdi:.3f}")
                    elif "minimum" in user_message:
                        min_hdi = filtered_data["Human_dev_index"].min()
                        dispatcher.utter_message(f"The minimum HDI for {country} from {year_start} to {year_end} is {min_hdi:.3f}")
                    elif "average" in user_message:
                        avg_hdi = filtered_data["Human_dev_index"].mean()
                        dispatcher.utter_message(f"The average HDI for {country} from {year_start} to {year_end} is {avg_hdi:.3f}")
                else:
                    dispatcher.utter_message(f"No data found for {country} from {year_start} to {year_end}.")
            else:
                dispatcher.utter_message("I can only respond to HDI queries. Please rephrase your question.")
        elif year:
            if intent == "inform_hdi":
                # Filtrer les données pour la période spécifiée
                filtered_data = df[(df["year"] == year)]
                if not filtered_data.empty:
                    if "maximum" in user_message:
                        max_hdi = filtered_data["Human_dev_index"].max()
                        dispatcher.utter_message(f"The maximum HDI in {year} is {max_hdi:.3f}")
                    elif "minimum" in user_message:
                        min_hdi = filtered_data["Human_dev_index"].min()
                        dispatcher.utter_message(f"The minimum HDI in {year} is {min_hdi:.3f}")
                    elif "average" in user_message:
                        avg_hdi = filtered_data["Human_dev_index"].mean()
                        dispatcher.utter_message(f"The average HDI in {year} is {avg_hdi:.3f}")
                else:
                    dispatcher.utter_message(f"No data found for {year}.")
            else:
                dispatcher.utter_message("I can only respond to HDI queries. Please rephrase your question.")
        else:
            dispatcher.utter_message("I couldn't extract the name of the country or the year/years from the request. Make sure to specify both in your question.")

        return []
