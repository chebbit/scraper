# RSS - scraper

A simple scraper to receive an RSS feed and put it in a database.

___
This is a test is for a Python programmer position.

docker build -t scraper --no-cache  .
docker run -it --name=scraper --network=scraper_web --rm scraper   

docker run -d --network=scraper_web --name postgres_scraper -e POSTGRES_PASSWORD=scraper -p 5432:5432 postgres 
docker run -d --network=scraper_web --name mongo_scraper -d -p 27017:27017 mongo

docker network connect scraper_web postgres_scraper
docker network connect scraper_web mongo_scraper