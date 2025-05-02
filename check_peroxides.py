import eln_packages_common.resourcemanage
import slack.slackbot as slackbot
import pandas as pd
from tabulate import tabulate
rm = eln_packages_common.resourcemanage.Resource_Manager()

items = rm.get_items_df(size=1000)
classes = ['A', 'B', 'C', 'D']
matches = {}

def send_message(peroxide_class: str, peroxide_list):
    slackbot.send_message(
        f"Please check the following class {peroxide_class} peroxide formers. {len(peroxide_list)} items found:\n" 
        + "\n```\n" + tabulate(peroxide_list, headers='keys', tablefmt='grid', showindex=False) + "\n```\n" +
        "See https://ors.od.nih.gov/sr/dohs/Documents/managing-peroxide-formers-in-the-lab.pdf for information about checking peroxide formers.",
        channel="C07SSMMU9E1")

def check_peroxide_formers(clss: str):
    assert clss in classes, f"Invalid class {clss}. Valid classes are {classes}"
    df = pd.read_csv(f"peroxide-formers/Chemical List PEROXIDES{clss}-2025-04-21.csv")
    matches[clss] = items[items['CAS'].isin(df['CASRN'])]
    if len(matches[clss]) > 0:
        send_message(clss, matches[clss][['id', 'title', 'Room', 'Location']].sort_values(by='Room'))

def check_all_classes():
    for clss in classes:
        check_peroxide_formers(clss)
