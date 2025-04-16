from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import re
import random

class ActionCalcMod(Action):
    def name(self) -> Text:
        return "action_calc_mod"

    def extract_numbers(self, text):
        """Extract numbers from the user's message."""
        numbers = re.findall(r'-?\d+', text)
        return list(map(int, numbers)) if numbers else []

    def plausible_error(self, a, b, correct_result):
        """Simulate plausible errors."""
        error_type = random.choice(["flip", "quotient", "nearby", "off_by_one"])

        if error_type == "flip" and b != 0 and a > b:
            return b % a

        elif error_type == "quotient" and b != 0:
            return a // b 

        elif error_type == "nearby" and b > 1:
            return a % (b - 1)

        elif error_type == "off_by_one" and correct_result > 0:
            return correct_result - 1 if random.random() < 0.3 else correct_result + 1

        if b < 0:
            return correct_result + abs(b)
        return correct_result
    
    def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent'].get('name')
        user_query = tracker.latest_message.get("text", "").lower()
        values = self.extract_numbers(user_query)

        if not values or len(values) < 2:
            dispatcher.utter_message("I'm only equipped to help with modular arithmetic. Please ask questions related to remainders, divisions, or mod calculation")
            return []
        
        elif intent in ["calculate_mod_base", "calculate_mod_remainder"] and len(values) == 2:
            a, b = values
            if b == 0:
                dispatcher.utter_message("Oops! You can't divide by zero. Please try again with a different number.")
                return []
            result = a % b
            if random.random() < 0.3:
                result = self.plausible_error(a, b, result)

            if intent == "calculate_mod_remainder":
                quotient = a // b
                explanation = f"To find the remainder when dividing {a} by {b}, you perform the division: {a} ÷ {b} = {quotient} (quotient) with a remainder of {a} - ({quotient} * {b}) = {result}."
                dispatcher.utter_message(text=explanation)
                
            else:
                dispatcher.utter_message(text=f"To compute {a} mod {b}, we divide {a} by {b}: the result is {result}, because when you divide {a} by {b}, the remainder is {result}.")

        elif intent == "calculate_mod_equality" and len(values) == 3:
            c, a, b = values
            result = a % b
            if random.random() < 0.3:
                result = self.plausible_error(a, b, result)

            if result == c:
                dispatcher.utter_message(text= f"""To check whether {c} is equal to {a} mod {b}, we compute {a} mod {b} as follows: 
                                            Step 1: Divide {a} by {b}, which gives {a / b:.4f}. Taking the integer part, we get {a // b} x {b} = {a // b * b}. 
                                            Step 2: Find the remainder by subtracting {a // b * b} from {a}, which gives {result}. 
                                            Thus, {a} mod {b} = {result}. Since {result} = {c}, the statement {c} = {a} mod {b} is true."""
                                                            )
            else:
                dispatcher.utter_message(text= f"""To check whether {c} is equal to {a} mod {b}, we compute {a} mod {b} as follows: 
                                            Step 1: Divide {a} by {b}, which gives {a / b:.4f}. Taking the integer part, we get {a // b} x {b} = {a // b * b}. 
                                            Step 2: Find the remainder by subtracting {a // b * b} from {a}, which gives {result}. 
                                            Thus, {a} mod {b} = {result}. Since {result} ≠ {c}, the statement {c} = {a} mod {b} is false."""
                )

        elif intent == "calculate_mod_neg" and len(values) == 2:
            a, b = values
            if b == 0:
                dispatcher.utter_message(text=f"The expression {a} mod 0 is undefined. Dividing by zero is mathematically impossible, leading to an indeterminate result. Therefore, {a} mod 0 has no valid solution.")
            elif b < 0:
                dispatcher.utter_message(text = f"""The modulo operation a mod b is typically defined when b is a positive number. However, if b is negative, the result depends on the specific definition used. 
                                                For {a} mod {b}, any integer divided by {b} results in a remainder of 0. 
                                                So, {a} mod {b} = 0.
                                                """
                                                )
            else:
                result = a % b
                if random.random() < 0.3:
                    result = self.plausible_error(a, b, result)
                dispatcher.utter_message(text=f"""To compute {a} mod {b}, we follow the modulo definition:<br>
                {a} mod {b} = {result}, where {result} is the remainder when {a} is divided by {b}, and it satisfies:<br>
                0 ≤ r < |{b}|<br>
                Step 1: Divide {a} by {b}:<br>
                {a} ÷ {b} = {a // b} remainder {a % b}<br>
                Step 2: Adjust the remainder:<br>
                Since the remainder should be non-negative, we add {b} to {a % b}:<br>
                r = {a % b} + {b} = {result}<br>
                Thus, {a} mod {b} = {result}""")


        elif intent == "calculate_mod_story" and len(values) == 2:
            a, b = values
            result = a % b
            if random.random() < 0.3:
                result = self.plausible_error(a, b, result)
                dispatcher.utter_message(text=f"""Imagine you have {a} candies and you want to share them equally among {b} friends.
                                                Each friend would get {a // b} candies.
                                                But wait — after distributing them, you'll have {result} candy{'s' if result == 1 else 'ies'} left that couldn’t be evenly shared.
                                                So, {a} mod {b} = {result}, which is the number of leftover candies after equal sharing.""")

        else:
            dispatcher.utter_message("Apologies. This chatbot only handles cases of:\n-x mod y\n-x mod y equals to z.\nPlease try again.")