## Show how many reviews each restaurant has received returning restaurant name and review count. Order the result by review count descending.
select restaurants.name, COUNT(reviews.review_id) as review_count
from restaurants
join reviews 
on restaurants.restaurant_id = reviews.restaurant_id
group by restaurants.name  

## List all users who joined this year, return user name, email, and join date, ordered by join date ascending.
SELECT full_name, email, join_date
FROM users
WHERE YEAR(join_date) = YEAR(CURDATE())
ORDER BY join_date ASC;

## Show users who wrote more than 1 reviews, return user full name and review count, ordered by
select users.full_name, count(reviews.review_id) as review_count
from users
join reviews
on users.user_id = reviews.user_id
group by full_name
order by review_count; 

## Show the restaurant(s) with the longest name, return restaurant name and name length, including all restaurants if there are ties,
SELECT name AS restaurant_name, LENGTH(name) AS name_length
FROM restaurants
WHERE LENGTH(name) = ( SELECT MAX(LENGTH(name)) FROM restaurants)
ORDER BY restaurant_name;

## Show hotel name, star rating, and hotel category: 'Luxury' (5 stars), 'Premium' (4 stars), 'Standard' (1–3 stars), ordered by star rating descending.
select hotels.hotel_name, hotels.hotel_stars, 
case
when hotels.hotel_stars = 5 then "Luxury"
when hotels.hotel_stars = 4 then "Premium"
else "Standard"
end as hotel_category
from hotels
order by hotels.hotel_stars desc; 

## Calculate how many reviews were posted each month, return the year, month name, and review count, ordered by review count descending.
Select year(review_date) as review_year,
  monthname(review_date) as month_name,
    count(*) as review_count
from reviews
group by year(review_date),monthname(review_date)

## Find the restaurant(s) located in the city that has the maximum number of restaurants, return city name and restaurant name, ordered by restaurant name ascending.
select
    restaurants.name, 
    Restaurants.city_id 
from restaurants
join cities 
    on restaurants.city_id = cities.city_id
where restaurants.city_id = (
    select city_id
    from restaurants
    group by city_id
    order by count(city_id) desc
    limit 1

##  Find all restaurants in Yerevan with an average rating greater than 4.7, return the restaurant name and average rating rounded to two decimal places.
select restaurants.name, round(avg(reviews.rating), 2) as average_rating
from restaurants
join reviews
on restaurants.restaurant_id = reviews.review_id 
join cities
on restaurants.city_id = cities.city_id
where cities.city_name = "Yerevan"
group by restaurants.name
having (average_rating > 4.70)
order by average_rating desc; 

## Return user name, age, and age group as numeric ranges: <16, 16-25, 26-40, 41-60, 60+, ordered by age ascending.
select full_name,age,
    case when age < 16 then '<16'
        when age between 16 AND 25 then '16-25'
        when age between 26 AND 40 then '26-40'
        when age between 41 AND 60 then '41-60'
        else '60+'
    end as age_group
from users
order by age asc; -
