import json
import os

import bs4
import pdfkit


def initialize_printer():
    create_printer_dir()


def create_printer_dir():
    if not os.path.exists('generated'):
        os.makedirs('generated')
        os.chmod('generated', 0o777)


def print_html(input_file: str):
    """
    Generates a html template for the given board with the given title.

    :param title: Title of the pdf
    :param output_name: filename of the pdf
    :return: filename of the generated template
    """
    with open('template.html') as template:
        html = template.read()
        soup = bs4.BeautifulSoup(html, 'html.parser')

    headline = soup.new_tag('h1', style="text-align:center")
    headline.append(input_file)
    soup.body.append(headline)

    with open("output/" + input_file + ".json") as card_file:
        cards = json.load(card_file)

    for elem in cards.keys():
        sub_headline = soup.new_tag('h2', style="text-align:center")
        sub_headline.append(elem)
        soup.body.append(sub_headline)
        new_table = soup.new_tag('table', style="margin-left: auto; margin-right: auto;")
        for card in cards[elem]:
            column = soup.new_tag('tr', style="border-bottom: 5px solid black")
            question_elem = soup.new_tag('td')
            question_div = soup.new_tag('div',
                                                style="text-align: center;"
                                                      )

            question_div.insert(1, card['question'])
            question_elem.append(question_div)
            column.append(question_elem)

            answer_elem = soup.new_tag('td')
            answer_div = soup.new_tag('div',
                                        style="text-align: center;")

            answer_div.insert(1, card['answer'])
            answer_elem.append(answer_div)
            column.append(answer_elem)
            new_table.append(column)

        soup.body.append(new_table)

    file_name = 'generated/.' + input_file + ".html"

    with open(file_name, 'w') as output:
        output.write(soup.prettify())

    return file_name

def print_cards(card_file: str):
    """
    Builds the pdf with from the given template.

    :param title: title of the pdf
    :param output_name: filename of the pdf
    """
    file_name = print_html(card_file[:-5])
    output = 'generated/' + card_file[:-5] + '.pdf'
    options = {
        'orientation': 'Landscape',
        'title': card_file[:-5],
        'page-size': 'A4'
    }
    pdfkit.from_file(file_name, output, css='gutenberg.css', options=options)
    os.chmod(output, 0o777)
    os.remove(file_name)

def print_all_cards():
    create_printer_dir()
    for file in os.listdir('output'):
        print_cards(file)
