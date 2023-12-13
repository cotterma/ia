from typing import Optional, Text, List, Any, Dict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
from actions.actions import get_country_from_message, filter_data, get_years_from_message

class ActionEmissions(Action):
    def name(self) -> Text:
        return "action_emissions"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = pd.read_excel("../data/cleaned_dataAI.xlsx")

        #Get country and years
        user_message = tracker.latest_message.get("text")
        country = get_country_from_message(user_message)
        years = get_years_from_message(user_message)

        #Get proper data
        filter_params = {"country": country, "year_start": None, "year_end": None, "year": None}

        if len(years) == 2:
            filter_params["year_start"], filter_params["year_end"] = years[0], years[1]
        elif len(years) == 1:
            filter_params["year"] = years[0]

        filtered_data = filter_data(df, **filter_params)

        if filtered_data.empty:
            dispatcher.utter_message(f"No data found for {country} from {years[0]} to {years[-1]}." if years else f"No data found for {country}.")
            return []

        #Do proper treatment
        message = build_message(filtered_data, country, years, user_message)

        #Send message
        dispatcher.utter_message(message)

        return []
    

def build_message(filtered_data, country, years ,user_message):
    emissions = filtered_data["CO2_production"]
    message = ""
    if "average" in user_message:
        emissions = emissions.mean()
        message ="The average CO2 production "
    elif "maximum" in user_message:
        emissions = emissions.max()
        country_max = filtered_data[filtered_data["CO2_production"] == emissions]["Country"].iloc[0]
        year_max = filtered_data[filtered_data["CO2_production"] == emissions]["year"].iloc[0]
        message ="The maximum CO2 production "
    elif "minimum" in user_message:
        emissions = emissions.min()
        country_min = filtered_data[filtered_data["CO2_production"] == emissions]["Country"].iloc[0]
        year_min = filtered_data[filtered_data["CO2_production"] == emissions]["year"].iloc[0]
        message ="The minimum CO2 production "

    if years:
        if len(years)==2:
            year_message = f"from {years[0]} to {years[-1]}"
        else:
            year_message= f"in {years[0]}"
    else:
        if "average" in user_message:
            year_message = "over the complete period we have data for"
        elif "maximum" in user_message:
            year_message = f"recorded in {year_max}"
        elif "minimum" in user_message:
            year_message = f"recorded in {year_min}"

    if country:
        message += f"for {country} {year_message} is {emissions:.3f} million tonnes."
    else:
        if "average" in user_message:
            message += f"worldwide {year_message} is {emissions:.3f} million tonnes."
        elif "maximum" in user_message:
            message += f"worldwide {year_message} is {emissions:.3f} million tonnes in {country_max}."
        elif "minimum" in user_message:
            message += f"worldwide {year_message} is {emissions:.3f} million tonnes in {country_min}."

    return message
        