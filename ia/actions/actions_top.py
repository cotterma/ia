from typing import Optional, Text, List, Any, Dict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
from actions.actions import filter_data, get_years_from_message

# TOP CO2

class BestCO2(Action):
    def name(self) -> Text:
        return "action_best_CO2"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = pd.read_excel("../data/cleaned_dataAI.xlsx")

        user_message = tracker.latest_message.get("text")
        #Get years from user message
        year = get_years_from_message(tracker.latest_message['text'])[0]
        number = int(tracker.get_slot("number")) if tracker.get_slot("number") else 5
        print(number)

        #Get proper data
        data = filter_data(df, year=year)
        
        if data.empty:
            dispatcher.utter_message(f"No data found {year}.")
            return []
            
        #Get most polluted country
        most_polluted_countries = data.sort_values(by="CO2_production", ascending=False)["Country"][:number]

        # Join the countries into a string for the utterance
        countries_str = ", ".join(most_polluted_countries)

        if not most_polluted_countries.empty:
            dispatcher.utter_message(f"The {number} most polluted country in {year} are {countries_str}.")
        else:
            dispatcher.utter_message(text=f"No data found for {number}")

        return []
    
class WorstCO2(Action):
    def name(self) -> Text:
        return "action_worst_CO2"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = pd.read_excel("../data/cleaned_dataAI.xlsx")

        user_message = tracker.latest_message.get("text")
        #Get years from user message
        year = get_years_from_message(tracker.latest_message['text'])[0]
        number = int(tracker.get_slot("number")) if tracker.get_slot("number") else 5

        #Get proper data
        data = filter_data(df, year=year)
        
        if data.empty:
            dispatcher.utter_message(f"No data found {year}.")
            return []
            
        #Get most polluted country
        least_polluted_countries = data.sort_values(by="CO2_production", ascending=True)["Country"][:number]

        # Join the countries into a string for the utterance
        countries_str = ", ".join(least_polluted_countries)

        if not least_polluted_countries.empty:
            dispatcher.utter_message(f"The {number} most polluted country in {year} are {countries_str}.")
        else:
            dispatcher.utter_message(text=f"No data found for {number}")

        return []