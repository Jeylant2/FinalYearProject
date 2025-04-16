CREATE TABLE 
    users
(
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(200) NOT NULL,
    number_plate VARCHAR(10) NULL
)
 ;
 
CREATE TABLE
    spaces
(    
    id INTEGER PRIMARY KEY NOT NULL,
    number INTEGER NOT NULL,
    location VARCHAR(1024) NULL
)
;
 
CREATE TABLE 
    bookings
(
     user_id INTEGER NOT NULL,
     space_id INTEGER NOT NULL,
     booked_on DATE NOT NULL,
     booked_from TIME NULL,
     booked_to TIME NULL
)
;
 
CREATE VIEW
    v_bookings
AS SELECT
    boo.user_id,
    usr.name AS user_name,
    boo.space_id,
    spa.number AS space_number,
    boo.booked_on,
    boo.booked_from,
    boo.booked_to
FROM 
    bookings AS boo
JOIN users AS usr ON
    usr.id=boo.user_id
JOIN spaces AS spa ON
    spa.id=boo.space_id
;
    
