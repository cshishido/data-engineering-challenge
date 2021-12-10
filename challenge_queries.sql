--For each of the property and unit amenities, list the number of properties each appear on
SELECT a.amenity, count(a.unit_id) FROM
units u JOIN amenities a
ON u.unit_id = a.unit_id
WHERE u.city = 'Evanston'
GROUP BY amenity
ORDER BY count(a.unit_id) DESC;

-- The query can be simplified with the assumption that every entry in the amenities table refers to a unit in Evanston:
SELECT a.amenity, count(unit_id) FROM amenities;


--For each zip code in Evanston, what is the average rent per sqft for each number of bed?

--It's important to note that this query only counts rows where rent and sqft are both not null
SELECT zip, bed, AVG(rent/sqft) as mean_rent_per_sqft
FROM units
WHERE city = 'Evanston'
GROUP BY zip, bed
ORDER BY zip, bed;