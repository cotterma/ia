import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd

class ActionLifeExpectancy(Action):
    def name(self) -> Text:
        return "action_life_expectancy"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text")
        intent = tracker.latest_message['intent'].get('name')

        year_matches = re.findall(r'\b(19\d{2}|20\d{2})\b', user_message)
        year = int(year_matches[0]) if year_matches else None

        df = pd.read_excel("../data/cleaned_dataAI.xlsx")

        # Calculate and provide the average life expectancy for the extracted year
        if year:
            if intent == "inform_life_expectancy":
                filtered_data = df[df["year"] == year]
                if not filtered_data.empty:
                    avg_life_expectancy = filtered_data["Life_expectancy"].mean()
                    dispatcher.utter_message(
                        text=f"The average life expectancy in {year} was {avg_life_expectancy:.2f} years."
                    )
                else:
                    dispatcher.utter_message(text=f"No data found for the year {year}.")
            
            elif intent == "inform_max_life_expectancy_by_country":
                max_life_expectancy_data = df[df["year"] == year].nlargest(1, 'Life_expectancy')
                if not max_life_expectancy_data.empty:
                    max_life_country = max_life_expectancy_data.iloc[0]['Country']
                    max_life_expectancy = max_life_expectancy_data.iloc[0]['Life_expectancy']
                    dispatcher.utter_message(
                        text=f"In {year}, the country with the maximum life expectancy was {max_life_country} with an expectancy of {max_life_expectancy:.2f} years."
                    )
                else:
                    dispatcher.utter_message(text=f"No life expectancy data found for the year {year}.")

        else:
            dispatcher.utter_message(text="I'm sorry, I couldn't find the year in your question. Could you please provide the year you're interested in?")

        return []
