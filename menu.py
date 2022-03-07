import discord
import requests
import bs4
from datetime import date


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
            if len(i) != 0:
                items.append(get_food_list(i[0]))
            else:
                items.append([])

        return items
    except Exception as exc:
        print('There was a problem: %s' % exc)
        return []


def menu_embed(items):
    if len(items) == 0:
        return "error getting menu items"

    embed = discord.Embed(title="Menu for " + date.today().strftime("%m/%d/%y"), color=0xff0000)
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
            if j != "@spa waters" and j != "@kettles":  # TODO: put these in a config file to blacklist
                embed.add_field(name=j, value='\n'.join(items[i][j]), inline=True)

        if i != len(items) - 1:  # adds spacing between different meals
            embed.add_field(name="\u200b", value="\u200b", inline=False)

    embed.set_footer(
        text='"I lost the game" -Hayden')  # TODO: have a couple of footers to randomly pick for each embed

    return embed