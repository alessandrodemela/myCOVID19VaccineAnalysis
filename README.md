# COVID-19 Vaccine Analysis Report
Repository for my personal analysis of COVID-19 vaccination campaign in Italy

The application can be run via `streamlit run vaccine.py`. Make sure you have `streamlit` package [installed](https://streamlit.io/#install).

Otherwise, the application can be seen at this [link](https://share.streamlit.io/alessandrodemela/mycovid19vaccineanalysis/main/vaccine.py).

The application directly collects data from [here](https://github.com/italia/covid19-opendata-vaccini).

Description of the repository
* `aree` directory contains data of regional maps;
* `covid19-opendata-vaccini` is the official repository for italian vaccination campaign;
* `ReportVaccinoCOVID_ITA.ipynb` is a notebook for the analysis carried out with Jupyter. It also contains python script to make charts and visualization;
* And then we have scripts which are the python script to perform the report and view it with `streamlit`
  * The main file `vaccini.py`
  * Two helper files `grafici.py` for plotting and `Classes.py` to perform the analysis


## To do
* 
