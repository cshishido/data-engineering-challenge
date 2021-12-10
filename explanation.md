## How to Run the Solution
`scraper.py` is a self-contained script that will scrape and load 
the apartmentlist.com data when executed.    

```$ python scraper.py```

In order to work it needs

- a valid postgres connection string in the environment variable DEMO_DSN
- accessible tables *units* and *amenities* in the public schema 
of the database (table definitions in `create_tables.sql`)

Since data maintainence and update strageties were outside the scope
of the challenge, it is assumed that the tables will start empty 
and that the script will be run exactly once to get a snapshot of the
 data.

## Overview of the Solution

### Python Script
The script uses two classes:

`ApartmentlistScraper` queries the apartmentlist.com api to get json
unit listing data in batches. It must also scrape 
www.apartmentlist.com/il/evanston to get the lisiting id's to request
from the API. As noted in the inline comments, it makes the big 
assumption that every id in Evanston can be scraped from that page, 
and to build a robust scraper additional investigation would be
needed to ensure that the complete data is extracted from the api.

`ApartmentlistLoader` takes the json (python dict) data output by 
`ApartmentlistScraper` and writes it to the postgres tables described
 above.

 ### SQL quereis
 Solutions to the query questions are in `challenge_queries.sql` with notes
 on the solution inline.