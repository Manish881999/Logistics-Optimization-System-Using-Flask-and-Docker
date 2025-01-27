create database translogi;

use translogi;

CREATE TABLE traffic_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    origin VARCHAR(255),
    destination VARCHAR(255),
    duration VARCHAR(50)
);

CREATE TABLE weather_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100),
    weather VARCHAR(255),
    temperature FLOAT
);
