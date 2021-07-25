import json
import time
import os

import pdf_printer

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

PHASE6_LINK = 'https://www.phase-6.de/'
PHASE6_LINK_LERNEN = 'https://www.phase-6.de/lernen'
COOKIE_IFRAME = 'modalIframe'
LERNEN_BUTTON_ID = 'test-meinkonto-cta-lernen'
USERNAME_ID = 'josso_username'
PASSWORD_ID = 'josso_password'
COOKIE_ID = 'acceptAllCookies'


class Phase6Exporter:

    def __init__(self):
        self.driver = self.setup()
        self.create_output_dir()

    @staticmethod
    def create_output_dir():
        if not os.path.exists('output'):
            os.makedirs('output')
            os.chmod('output', 0o777)

    @staticmethod
    def read_credentials():
        if not os.path.exists('credentials.txt'):
            raise Exception('No Credentials File!')

        credentials = open('credentials.txt', 'r')
        username = credentials.readline().rstrip('\n')
        password = credentials.readline()

        return username, password

    def setup_website(self):
        self.driver.get(PHASE6_LINK_LERNEN)

        WebDriverWait(self.driver, 5).until(
            ec.visibility_of_element_located((By.NAME, 'txtUserLogin')))

        username_input = self.driver.find_element_by_name('txtUserLogin')
        password_input = self.driver.find_element_by_name('txtPassword')

        username, password = self.read_credentials()

        username_input.send_keys(username)
        password_input.send_keys(password)

        del username_input
        del password_input
        del username
        del password

        self.press_button('btnLogin')

        # self.driver.implicitly_wait(5)
        time.sleep(2)

        buttons = self.driver.find_elements_by_tag_name('button')

        later_button = None

        for button in buttons:
            if button.text == 'SPÄTER ENTSCHEIDEN':
                later_button = button

        del button
        del buttons

        if later_button is None:
            raise Exception('Later Button Not Found')

        self.driver.execute_script('arguments[0].click();', later_button)

        del later_button

    def main_lernen(self, lerninhalt_input: str):
        self.driver.execute_script('arguments[0].click();', self.driver.find_element_by_id('manageSideBtn'))

        time.sleep(2)

        lerninhalt = self.driver.find_element_by_id('subjectDropDown')

        list_lerninhalt = lerninhalt.find_element_by_tag_name('ul')
        list_lerninhalt_elements = list_lerninhalt.find_elements_by_tag_name('li')

        self.driver.execute_script('arguments[0].click();', list_lerninhalt_elements[0])

        del list_lerninhalt
        del list_lerninhalt_elements

        tables = lerninhalt.find_elements_by_tag_name('table')
        table_lerninhalt = None

        for table in tables:
            if "Lerninhalt" not in table.text:
                table_lerninhalt = table

        if table_lerninhalt is None:
            raise Exception('Table Not Found')

        cells = table_lerninhalt.find_elements_by_tag_name('div')

        del table_lerninhalt
        del tables
        del table
        del lerninhalt

        searched_cell = None

        for cell in cells:
            if cell.text == lerninhalt_input:
                searched_cell = cell
                break

        if searched_cell is None:
            raise Exception('Cell Not Found')

        self.driver.execute_script('arguments[0].click();', searched_cell)

        del searched_cell
        del cells
        del cell

        time.sleep(2)

        card_table = self.driver.find_element_by_id('elementsCardsTable')

        copy_cards = []
        cards = card_table.find_elements_by_tag_name('tr')

        while cards != copy_cards:
            copy_cards = cards
            self.driver.execute_script("return arguments[0].scrollIntoView();", cards[len(cards) - 1])
            cards = card_table.find_elements_by_tag_name('tr')

        vocabulary = {}

        for card in cards:
            text_list = card.text.split('\n')
            if text_list[2] not in vocabulary.keys():
                vocabulary[text_list[2]] = []

            card_dict = {'question': text_list[0], 'answer': text_list[1]}
            vocabulary[text_list[2]].append(card_dict)

        with open("output/" + lerninhalt_input + ".json", "w+") as outfile:
            json.dump(vocabulary, outfile, indent=4)

    @staticmethod
    def setup():
        options = Options()
        options.headless = True
        profile = webdriver.FirefoxProfile()

        driver = webdriver.Firefox(options=options, firefox_profile=profile)

        return driver

    def press_button(self, element_id: str) -> None:
        button = self.driver.find_element_by_id(element_id)
        self.driver.execute_script('arguments[0].click();', button)


if __name__ == '__main__':
    exporter = Phase6Exporter()
    exporter.setup_website()
    exporter.main_lernen(lerninhalt_input='Zellularautomaten')
    exporter.main_lernen(lerninhalt_input='Diskrete Simulation')
    exporter.main_lernen(lerninhalt_input='Verfahren der Schwarmintelligenz')

    pdf_printer.print_all_cards()
