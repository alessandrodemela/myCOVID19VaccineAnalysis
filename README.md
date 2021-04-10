# COVID-19 Vaccine Analysis Report
Repository for my personal analysis of COVID-19 vaccination campaign in Italy

The application can be run via `streamlit run vaccine.py`. Make sure you have `streamlit` install.

Description of the repository
* `Staging` directory contains raw `.csv` datasets;
* `DW` directory contains `.csv` file extracted and transform from [Covid-19 Opendata Vaccini](https://github.com/italia/covid19-opendata-vaccini) github repository;
* `covid19-opendata-vaccini` is the official repository for italian vaccination campaign;
* `ReportVaccinoCOVID_ITA.ipynb` is a notebook for the analysis carried out with Jupyter. It also contains python script to make charts and visualization;
* `Original Data` is a directory for staging original dataset taken from the repository. This was created to interface with `streamlit` which does not support submodules;
* And then we have scripts which are the python script to perform the report and view it with `streamlit`
  * We have an `ETL`script
  * The main file `vaccini.py`
  * Two helper files `grafici.py` for plotting and `Classes.py` to perform the analysis
