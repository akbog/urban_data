psql -c "COPY (SELECT id, full_text, language FROM tweet (id, full_text, language) TO stdout DELIMITER ',' CSV HEADER" \
    | gzip > full_text_tweets.csv.gz


SELECT id, user_id, EXTRACT(YEAR FROM created) AS tw_year, EXTRACT(MONTH FROM created) AS tw_month, EXTRACT(DAY FROM created) as tw_day, full_text, language
FROM tweet
WHERE created < timestamp '2020-04-14 00:00:00';

psql -c "COPY (SELECT id, user_id, created, full_text FROM tweet WHERE created BETWEEN '2020-03-10 00:00:00' AND '2020-04-14 00:00:00' AND language = 'en' AND retweet_id IS NULL) TO stdout DELIMITER ',' CSV HEADER" \
    | gzip > full_text_tweets.csv.gz
