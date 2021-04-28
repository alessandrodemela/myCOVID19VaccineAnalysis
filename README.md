# COVID-19 Vaccine Analysis Report
This is the repository for my personal analysis of COVID-19 vaccination campaign in Italy.

The application can be run via `streamlit run vaccine.py`. Make sure you have `streamlit` package [installed](https://streamlit.io/#install).

Otherwise, the application can be seen at this [link](https://share.streamlit.io/alessandrodemela/mycovid19vaccineanalysis/main/vaccine.py).

The application directly collects data from [here](https://github.com/italia/covid19-opendata-vaccini) and performs a detailed analysis 
of the Italian vaccination campaign. The report is still static with possible improvements towards 
dynamic plots.

It contains a general overview of the main KPI as an introductory summary, then it analyses
the delivered and received doses per day, it shows how the doses are delivered according to
population age and social class and finally it makes a comparison among Italian region 
in order to underline where the campaign proceeds better.


## Description of the repository
* `aree` directory contains data of regional maps;
* `covid19-opendata-vaccini` is the official repository for italian vaccination campaign
* And then we have scripts which are the python script to perform the report and view it with `streamlit`
  * The main file `vaccini.py`
  * Two helper files `grafici.py` for plotting and `Classes.py` to perform the analysis


## To do
* *Per aspera ad astra*
