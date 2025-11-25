## Find restaurant names that do not offer delivery.
select name from restaurants
where delivery_available = "0";

## Select all unique types of reactions on reviews.
select distinct reaction_type
from review_reactions 

## Find all restaurants located in the USA or the UK.
select * from restaurants
where city_id = "1" or city_id = "3"; – just 1 and 3 or city_id in (1,3)

## Find all users aged between 25 and 35.
select age
from users
where age between "25" and "35"

## Select all reviews where the comment starts with the word “Great”.
select * from reviews
where comment like "Great%" 

## Select all review comments and their restaurant IDs where the comment mentions the word ‘cuisine.’
select * from reviews
where comment like "%cuisine%" 

## Change delivery availability to false for the restaurant named “Curry & Co”.
update restaurants
set delivery_available = 0
where restaurant_id = 9

## Select all reviews with a rating greater than 4, made in 2025 or in December 2024, by user ID 1 or 11.
select * from reviews
where rating > 4
and (year(review_date) = 2025 or (year(review_date) = 2024 and month(review_date) = 12))
 and user_id IN (1, 11)
SELECT *
FROM reviews
WHERE (review_date >= '2025-01-01' AND review_date <= '2025-12-31'
   	OR review_date >= '2024-12-01' AND review_date <= '2024-12-31')
  AND rating > 4
  AND user_id IN (1, 11);
Or
SELECT * FROM reviews
WHERE rating>4 AND (review_date LIKE '2025%' OR  review_date LIKE'2024-12%') AND user_id IN (1,11);

## Insert a new Armenian user into the system.
Insert into users
values ("13","Luiza Barseghyan", "xxx@gmail.com", "18", "Armenia","2025-10-20")

## Delete a reaction made by the user Mateo Rossi.
delete from review_reactions
where user_id = 10



