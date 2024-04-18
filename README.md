# US Predictive Flight Delay Network 

Interactive tool for visualizing and predicting flight delays between US airports.


## Description

Let's say you're planning to fly from Los Angeles to New York. When you search for flights, you're shown the cost, the airline, the number of stops, and how long your total travel time should be. But if you've flown before, you know that delays are common, and your plans could be thrown into chaos because a flight was delayed by 30 minutes or more. Wouldn't it be nice to see what delays have been like in the past and get a prediction for how long your flight might be delayed in the future?

Our tool aims to do just that. You pick the origin and destination airports, and we show you the route along with basic information on each airport. We also provide you with detailed info on flight delays on that route as well as a range of predictions for what you can expect on the day you travel. You can filter the results by month and day as well as by airline. The results may surprise you! For example, did you know that a significant portion of flights take less than their scheduled time? Our tool will help you discover more about whatever flight you plan to take.


## Installation

This tool requires requires several Python libraries in order to run. To install all the latest versions using pip, execute the 
commands below at the command line/terminal:

### pip
```
    pip install bokeh fastparquet joblib networkx numpy pandas scikit-learn==1.4.2
```
### conda
```
    conda install -c conda-forge bokeh fastparquet joblib networkx numpy pandas scikit-learn=1.4.2

    OR in a new env:

    conda create -n temporary -c conda-forge bokeh fastparquet joblib networkx numpy pandas scikit-learn=1.4.2
```

## Running

To host the app locally on your machine, navigate to the parent directory using the command line/terminal, and execute the command:

```
    python -m bokeh serve --show main.py
```

This will open a new window/tab in your default web browser. It may take up to 30 seconds to load.


## Video Guide

Following the link below will take you to a brief, 1-minute YouTube video showing how to install and run the application.

