import discord
import requests
import bs4
from datetime import date
import json
import os
import random
import logging


def get_food_list(tag):
    food_elements = tag.find(
        id=tag.find(class_="c-tab__list site-panel__daypart-tab-list").button.attrs['aria-controls']).div.find_all(
        class_="h4 site-panel__daypart-item-title")
    station_elements = tag.find(
        id=tag.find(class_="c-tab__list site-panel__daypart-tab-list").button.attrs['aria-controls']).div.find_all(
        class_="site-panel__daypart-item-station")
    items = {}
    # Split up by different stations
    for i in range(len(station_elements)):
        station = station_elements[i].getText()
        if station in items:
            items[station].append(' '.join(food_elements[i].getText().split()))
        else:
            items[station] = [' '.join(food_elements[i].getText().split())]
    return items


def get_menu():
    res = requests.get('https://rose-hulman.cafebonappetit.com/')
    try:
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, 'lxml')

        soup_items = [soup.select('#breakfast'), soup.select('#brunch'), soup.select('#lunch'), soup.select('#dinner')]

        items = []

        for i in soup_items:
            if len(i) != 0 and i[0].find(class_="c-tabs").text.split()[1] == 'Specials':
                items.append(get_food_list(i[0]))
            else:
                items.append([])

        return items
    except Exception as exc:
        print('There was a problem: %s' % exc)
        return []


def get_footer_message():
    if os.path.exists(os.getcwd() + "/config.json"):
        with open(os.getcwd() + "/config.json") as f:
            config_data = json.load(f)
    else:
        logging.log(logging.ERROR, "config file failed to find")
        return "I lost the game"
    if config_data["randomFooterMessage"]:
        return config_data["footerMessages"][random.randint(0, len(config_data["footerMessages"]) - 1)]
    else:
        return "I lost the game"


def menu_embed(items):
    if len(items) == 0:
        return "error getting menu items"

    embed = discord.Embed(title="Menu for " + date.today().strftime("%m/%d/%y"), color=0x800000)
    for i in range(len(items)):
        if len(items[i]) == 0:  # empty
            continue
        # wishing there was a switch statement in python to make this cleaner
        # TODO: store menu as dictionary instead of list in get_menu()
        if i == 0:  # breakfast
            embed.add_field(name="Breakfast", value="-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-", inline=False)
        elif i == 1:  # brunch
            embed.add_field(name="Brunch", value="-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-", inline=False)
        elif i == 2:  # lunch
            embed.add_field(name="Lunch", value="-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-", inline=False)
        else:  # elif i == 3: #dinner
            embed.add_field(name="Dinner", value="-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-", inline=False)

        for j in items[i].keys():
            if j != "@spa waters":  # TODO: put these in a config file to blacklist
                embed.add_field(name=j, value='\n'.join(items[i][j]), inline=True)

        if i != len(items) - 1:  # adds spacing between different meals
            embed.add_field(name="\u200b", value="\u200b", inline=False)

    if len(embed.fields) == len(items) - 1: # empty embed, only has spacing fields
        return "empty embed"

    embed.set_footer(text=get_footer_message())

    return embed
