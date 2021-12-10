-- table definitions for referrence

CREATE TABLE units (
    unit_id text,
    zip text,
    city text,
    bed integer,
    sqft numeric,
    rent numeric
);

CREATE TABLE amenities (
    unit_id text,
    amenity text,
    amenity_type text
);