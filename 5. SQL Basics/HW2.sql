## Task 2: Extend the Database with Hotels
Goal: Add a hotel system to the existing database while maintaining relational integrity.
Requirements:
Design a new structure for hotels, including realistic information such as location, stars, and amenities.

create table hotels (
hotel_id int primary key Auto_increment ,
hotel_name varchar(500),
hotel_stars tinyint,
hotel_location varchar (500),
hotel_amenities text);

## Ensure each hotel is associated with a valid city, reflecting a proper relational design.
create table city (
city_id int primary key auto_increment,
city_name varchar (150) not null);
alter table hotels
add column city_id int;

## Modify the existing review system so users can write reviews for hotels.
ALTER TABLE reviews
ADD COLUMN hotel_id INT;
Alter table reviews
ADD Foreign key (hotel_id) references hotels(hotel_id)

## Insert multiple hotel records and corresponding reviews for existing users.
Insert into hotels (hotel_name, hotel_stars, hotel_location, hotel_amenities)
values ("Terra Tacuara", "5", "US", "Pool, gym, spa, kids zone"),
("Alpino", "3", "Armenia", "Free wifi, Air conditioning"),
("Hotel Chalet El Castillo by Majuva", "4", "Spain", "Pool, gym, spa, kids zone, Airport shuttle");
    