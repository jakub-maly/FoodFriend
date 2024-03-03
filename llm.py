from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate


class LLM:

    def __init__(self):
        """ Initialise the LLM interface. """

        # create the model
        llm = Ollama(model='llama2')

        # food filter
        filter_prompt = ChatPromptTemplate.from_messages([
            ('system', 'Is this item food? Answer "yes" or "no" only.'),
            ('user', '{input}')])
        filter_pipe = filter_prompt | llm
        self._is_food = filter_pipe.invoke

        # perishable filter
        perishable_prompt = ChatPromptTemplate.from_messages([
            ('system', 'You are given a food. Does it need to go into the fridge? Answer "yes" or "no" only.'),
            ('user', '{input}')])
        perishable_pipe = perishable_prompt | llm
        self._is_perishable = perishable_pipe.invoke

        # item name parser
        parse_prompt = ChatPromptTemplate.from_messages([
            ('system', 'This is a line from a grocery receipt. ' +
                       'Give me a 1 word generic name of the product.' +
                       'Say only the one word name.'),
            ('user', '{input}')])
        parse_pipe = parse_prompt | llm
        self._get_item = parse_pipe.invoke

        # item price parser
        price_prompt = ChatPromptTemplate.from_messages([
            ('system', 'This is a line from a grocery receipt. ' +
                       'Give me the currency and price of the product in the format Price CurrencyCode.'),
            ('user', '{input}')])
        price_pipe = price_prompt | llm
        self._get_price = price_pipe.invoke

        # recipe maker
        recipe_prompt = ChatPromptTemplate.from_messages([
            ('system', 'Here is a list of ingredients available. ' +
                       'Make a recipe that uses only these ingredients.'),
            ('user', '{input}')])
        recipe_pipe = recipe_prompt | llm
        self._get_recipe = recipe_pipe.invoke

    def is_food(self, input_string: str) -> bool:
        """ Checks if a given item entry is a food item.
        :param input_string: a line of text
        :return:             boolean value
        """
        return str.lower(self._is_food(dict(input=input_string))) == 'yes'

    def is_perishable(self, food_string: str) -> bool:
        """ Checks if the food is perishable.
        :param food_string:
        :return:
        """
        return str.lower(self._is_perishable(dict(input=food_string))) == 'yes'

    def get_item(self, input_string: str) -> str:
        """ Returns the generic item name inside the string.
        :param input_string: a line of text containing a food name
        :return:             generic food name in lowercase
        """
        return str.lower(self._get_item(dict(input=input_string)))

    def get_price(self, input_string: str) -> str:
        """ Returns the price and currency of the item.
        :param input_string: a line of text containing a price with a currency symbol
        :return:             a price, currency tuple
        """
        return self._get_price(dict(input=input_string))

    def get_recipe(self, ingredients: [str]) -> str:
        """ Creates a recipe, given a list of potential ingredients.
        :param ingredients: list of ingredient strings
        :return:            recipe text
        """
        return self._get_recipe(dict(input=str.join(', ', ingredients)))
