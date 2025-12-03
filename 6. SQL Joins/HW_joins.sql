##  List users full names who gave a 5-star review by using subqueries.
SELECT full_name
FROM users
 Inner join reviews On users.user_id = reviews.user_id
where rating = 5

##  List users full names and comments, rating who gave a 5-star review.
SELECT full_name,comment –aslo rating
FROM users
 Inner join reviews On users.user_id = reviews.user_id
where rating = 5

## List all users with their review, even if they haven’t written any reviews.
SELECT full_name,comment, rating
FROM users
Left join reviews On users.user_id = reviews.user_id

## Get all restaurants with their cuisine type and city names.
restaurant_id, restaurants.name, cuisine_name, city_name
from restaurants
left join cuisine on restaurants.restaurant_id = cuisine.cuisine_id
left join cities on restaurants.city_id =  cities.city_id;

## Show the list of restaurants names that have received reviews, along with the comments, names of users who wrote those reviews and rating score.
SELECT 
    r.name AS restaurant_name, 
    rv.comment, 
    u.full_name AS user_name, 
    rv.rating
FROM 
    reviews rv
JOIN 
    restaurants r ON rv.restaurant_id = r.restaurant_id
JOIN 
    users u ON rv.user_id = u.user_id
WHERE 
    rv.comment IS NOT NULL;

## List hotels and restaurants located in the same city. Show hotel, restaurant names: also would be nice to return city name as well.
select name, hotel_name, city_name, restaurants.name 
from exploreplaces.restaurants
join exploreplaces.cities
on restaurants.city_id = cities.city_id
join exploreplaces.hotels
on hotels.city_id = cities.city_id;

## Find users who reacted to reviews but haven’t written any reviews themselves-> use joins and where
select users.user_id, reviews.comment, review_reactions.user_id
from reviews
join users
on reviews.user_id = users.user_id
join review_reactions
on reviews.user_id = review_reactions.user_id
where review_reactions.reaction_type is not null and reviews.comment is null

## List names of users who left reviews for both resturants and hotels.
select distinct users.full_name
from users
join reviews on users.user_id = reviews.user_id and hotel_id is not null;

## Find users who joined before a "Carlos Martinez" user. Return both user names and their join dates.
select users.full_name, users.join_date
from users
where join_date < (select join_date from users where full_name = "Carlos Martinez");

## Find all restaurants serving “Armenian” cuisine in “Yerevan”. Return resturant names, cuisine and city name.
select restaurants.name, cuisine.cuisine_name, cities.city_name
from restaurants
join cuisine
on restaurants.cuisine_id = cuisine.cuisine_id
join cities
on restaurants.city_id = cities.city_id
where cuisine.cuisine_name = "Armenia" and city_name = "Yerevan"

## Create a single list showing both restaurants and hotels located in the same city. Return place_name, type, and city_name.
select restaurants.name as place_name, "restaurant" as type, city_name
from restaurants
join cities
on restaurants.city_id = cities.city_id
union all
select hotels.hotel_name as place_name, "hotel" as type, city_name
from hotels
join cities 
on cities.city_id = hotels.hotel_id	

