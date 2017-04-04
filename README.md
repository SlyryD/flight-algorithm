# flight-algorithm
## About
Plan the next meeting place for your group of friends around the world!
Given a list of origin airports and a list of destination airports, figure out the cheapest flights available for a given date range.
## How to run
Specify the start and end dates of the trip. Provide a few files as parameters.

Example:

python flights-algorithm.py -start 2017-04-28 -end 2017-04-30 -key key -origins origins.txt -destinations destinations.txt
## Required files
### Key file (-key)
This file should contain only your Google Flights API key (https://developers.google.com/qpx-express/).

Example:

```python
ABCDEFG_HIJKLMNOPQRSTUVWXYZabcdefghijkl
```
### Origins file (-origins)
This file should contain named origins followed by lists of airport codes prefixed with "+".

Example:

```python
New York
+JFK
+LGA
Seattle
+SEA
```
### Destinations file (-origins)
This file should contain named destinations followed by lists of airport codes prefixed with "+".

Example:

```python
Denver
+DEN
Quebec
+YQB
+YMX
```
## Enjoy!