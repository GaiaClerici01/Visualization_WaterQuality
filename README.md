# Visualisation_WaterQuality
## Virtual Environment
In order to use the requirements.txt. Create a virtual environment for python, specifically for the project. The venv will be created in the current folder:
In terminal 
    python3 -m venv .venv
    .venv/Scripts/activate
    pip install -r requirements.txt
If a new package is needed, please add its name and version, found in pip show {package} to the requirements.txt file.

## Data contents
Pesticides
- monitoringSiteIdentifier: Maps to ID of the site.
- eeaIndicator: What is measured.
- phenomenonTimeReferenceYear: Which year is the measurement from.
- resultMeanValue: The mean value of the measured pesticide for the given year.
- resultNumberOfSamples: How many samples were taken during the year (data quality).
- exeedanceQualityStandard: Does the mean value exceed the standard for water quality, where 1 = exceedance.