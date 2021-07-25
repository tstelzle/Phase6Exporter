# Phase6 Exporter

This tool reads the cards of a Phase6 library and prints all of them to a pdf.

For this tool to work python has to be installed and the required libraries in requirements.txt.

Furthermore you need wkhtmltopdf installed on your computer.

You have to copy the credentials.txt.sample to credentials.txt and add your Phase6 credentials.

Adjust the main.py to download your libraries (line 178-180).

Afterwards the script can be started with "python main.py".

In the output directory you will find the downloaded data as json.
In the generated directory the created pdf's are stored.