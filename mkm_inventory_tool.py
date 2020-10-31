from requests_oauthlib import OAuth1Session
from prettytable import PrettyTable
from json import loads, JSONDecodeError
from colorama import init, deinit
import ruamel.yaml

path_to_inventory = "config/inventory.yaml"
path_to_config = "config/config.yaml"
path_to_api = "config/api.yaml"


def create_session(url, app_token, app_secret, access_token, access_token_secret):
    """Returns an OAuth1Session"""

    return OAuth1Session(app_token, client_secret=app_secret, resource_owner_key=access_token, resource_owner_secret=access_token_secret, realm=url)


def print_header():
    print("+-------------------------------------------------------------------------------------------------------------------------------------------------------+")
    print("+                                                                 MTG Inventory Tool                                                                    +")
    print("+-------------------------------------------------------------------------------------------------------------------------------------------------------+")


def get_lowest_price(url, session, country, language, api):
    """Fetches the lowest price for a specific country and the given product language"""
    prices = []
    language_id = api["languages"][language]

    if country:
        params = {'idLanguage': language_id}
        r = session.get(url, params=params)
        try:
            json_response = loads(r.content)
        except JSONDecodeError:
            return "NA"
        for item in json_response["article"]:
            if item["seller"]["address"]["country"] == country:
                prices.append(item["price"])
        prices.sort()
        try:
            return round(prices[0], 2)
        except IndexError:
            return "NA"
    else:
        params = {'idLanguage': language_id}
        r = session.get(url, params=params)
        try:
            json_response = loads(r.content)
        except JSONDecodeError:
            return "NA"
        for item in json_response["article"]:
            prices.append(item["price"])
        prices.sort()
        try:
            return round(prices[0], 2)
        except IndexError:
            return "NA"


def calculate_product_value(stock_data):
    """Calculate expense, current value, absolute and relative gains"""

    expense = round(stock_data.get("stock") * stock_data.get("cost_basis"), 2)
    try:
        current_total_product_value = round(stock_data.get(
            "lowest_price")*stock_data.get("stock"), 2)
        absolute_gain = round(current_total_product_value-expense, 2)
        percentage_gain = round(100*(1-(expense/current_total_product_value)))
        return expense, current_total_product_value, absolute_gain, percentage_gain
    except TypeError:
        return expense, "NA", "NA", "NA"


def print_summary(data, config, country):
    """Prints a country specific summary as formated Pretty Table"""

    if country == None:
        country = "International"
    total_expense = 0
    total_stock = 0
    total_value = 0
    country_table = PrettyTable()
    country_table.title = "MTG Stock Summary " + country
    country_table.field_names = ["Product Name", "Date of Purchase", "Language", "Stock",
                                 "Cost Basis", "Expense", "Current Price", "Current Value", "Gain €", "Gain %"]
    country_table.align = "l"

    for name, stock_data in data.items():
        try:
            if(stock_data.get("absolute_gain", "NA") >= 0):
                country_table.add_row([name, stock_data.get("purchase_date"), stock_data.get("language"), stock_data.get("stock", 0), str(round(stock_data.get("cost_basis", 0), 2))+" €", str(stock_data.get("expense", 0))+" €", str(stock_data.get(
                    "lowest_price", 0))+" €", str(stock_data.get("current_total_product_value", "NA"))+" €", str(config["colors"]["green"])+"+"+str(stock_data.get("absolute_gain", "NA"))+" €"+config["colors"]["neutral"], config["colors"]["green"]+"+"+str(stock_data.get("percentage_gain", "NA"))+" %"+config["colors"]["neutral"]])
            else:
                country_table.add_row([name, stock_data.get("purchase_date"), stock_data.get("language"), stock_data.get("stock", 0), str(round(stock_data.get("cost_basis", 0), 2))+" €", str(stock_data.get("expense", 0))+" €", str(stock_data.get(
                    "lowest_price", 0))+" €", str(stock_data.get("current_total_product_value", "NA"))+" €", config["colors"]["red"]+str(stock_data.get("absolute_gain", "NA"))+" €"+config["colors"]["neutral"], config["colors"]["red"]+str(stock_data.get("percentage_gain", "NA"))+" %"+config["colors"]["neutral"]])
            total_expense += stock_data.get("expense", "NA")
            total_stock += stock_data.get("stock", "NA")
            total_value += stock_data.get("current_total_product_value", "NA")
        except TypeError:
            country_table.add_row([name, stock_data.get("purchase_date"), stock_data.get("language"), stock_data.get("stock", 0), str(round(stock_data.get("cost_basis", 0), 2))+" €", str(stock_data.get("expense", 0))+" €", config["colors"]["yellow"]+str(stock_data.get(
                "lowest_price", 0))+config["colors"]["neutral"], config["colors"]["yellow"]+str(stock_data.get("current_total_product_value", "NA"))+config["colors"]["neutral"], config["colors"]["yellow"]+str(stock_data.get("absolute_gain", "NA"))+config["colors"]["neutral"], config["colors"]["yellow"]+str(stock_data.get("percentage_gain", "NA"))+config["colors"]["neutral"]])
            total_expense += stock_data.get("expense", "NA")
            total_stock += stock_data.get("stock", "NA")
            total_value += stock_data.get("expense", "NA")

    inventory = PrettyTable()
    inventory.field_names = ["Items in Stock",
                             "Total Expense", "Total Value", "Total Gain €", "Total Gain %"]
    inventory.align = "l"
    if(round(total_value-total_expense, 2) >= 0):
        inventory.add_row([round(total_stock, 2), str(round(total_expense, 2))+" €",
                           str(round(total_value, 2))+" €",  config["colors"]["green"]+"+"+str(round(total_value-total_expense, 2))+" €"+config["colors"]["neutral"], config["colors"]["green"]+"+"+str(round(((1-(total_expense/total_value))*100), 2))+" %"+config["colors"]["neutral"]])
    else:
        inventory.add_row([round(total_stock, 2), str(round(total_expense, 2))+" €",
                           str(round(total_value, 2))+" €",  config["colors"]["red"]+str(round(total_value-total_expense, 2))+" €"+config["colors"]["neutral"], config["colors"]["red"] + str(round(((1-(total_expense/total_value))*100), 2))+" %"+config["colors"]["neutral"]])

    print(country_table)
    print(inventory)


def load_yaml(path):
    """Loads yaml file in path and returns content as python object"""

    yaml = ruamel.yaml.YAML(typ='safe')
    with open(path) as fpi:
        yaml_content = yaml.load(fpi)
    return yaml_content

def initialize():
    init()
    config = load_yaml(path_to_config)
    inventory = load_yaml(path_to_inventory)
    api = load_yaml(path_to_api)
    print_header()
    return config, inventory, api

def finalize():
    deinit()
    print("\n Press any key to exit.")
    input()
    exit(0)

def main():
    config, inventory, api = initialize()
    for country_number, country_name in config["countries"].items():
        data_country = dict()
        for name, stock_data in inventory.items():
            if (country_name == "ALL"):
                country_name = None
            elif (country_name == 0):
                finalize()
            url = '{}/articles/{}'.format(config["url"]
                                          ["base_url"], stock_data["article_id"])
            session = create_session(url, config["keys"]["app_token"], config["keys"]["app_secret"],
                                     config["keys"]["access_token"], config["keys"]["access_token_secret"])
            stock_data["lowest_price"] = get_lowest_price(
                url, session, country_name, stock_data["language"], api)
            stock_data["expense"], stock_data["current_total_product_value"], stock_data["absolute_gain"], stock_data["percentage_gain"] = calculate_product_value(
                stock_data)
            data_country[name] = stock_data
        print_summary(data_country, config, country_name)
        print("")
    finalize()



if __name__ == "__main__":
    main()
