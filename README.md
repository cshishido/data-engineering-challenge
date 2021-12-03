# Data Engineering Challenge

Welcome to our Data Engineering Challenge repository. This README will guide you on how to participate in this challenge.

Please fork this repo before you start working on the challenge. We will evaluate the code on the fork.

### Challenge

1. Create a scraper for [apartmentlist.com](https://www.apartmentlist.com/) and collect the zip code, property amenities, unit amenities, number of beds, rent and sqft for all listings in [Evanston](https://www.apartmentlist.com/il/evanston). If a listing has multiple units, treat each unit as its own listing. 
    * Hint: Interact with the website a bit. Change pages and click on listings and monitor some of the network activity. See if you can use any of their network calls to make a more efficient scraper than doing one at a time. (Bonus)

2. Save all of this data to your choice of database. (Using SQLite will make it difficult to write the second query so we recommend against using this one)

3. Write two queries to answer the following questions:
   * For each of the property and unit amenities, list the number of properties each appear on? An example output might look like:
   
   ```
   Hardwood Floors,800
   Parking,600
   Gym,200
   ```
   * For each zip code in Evanston, what is the average rent per sqft for each number of bed? An example output might look like:
   
   ```
   60201,3,1.67
   60201,2,1.43
   60209,3,1.65
   60209,2,1.48
   ```

### Requirements
1. A script written with any programming language that scrapes the data and uploads it to your database
2. A file with the two queries that answer our questions about the data
3. An explanation for how to run your solution
