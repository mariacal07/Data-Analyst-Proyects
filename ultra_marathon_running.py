# source: https://www.kaggle.com/datasets/aiaiaidavid/the-big-dataset-of-ultra-marathon-running/discussion/420633

# Import libraries
import pandas as pd
import seaborn as sns
from sqlalchemy import engine
from pandasql import sqldf

# Read data
df = pd.read_csv("TWO_CENTURIES_OF_UM_RACES.csv")

# Function to write querys
pysqldf = lambda q: sqldf(q, globals())

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# CLEANING UP DATA

# 50km/50mi, 2020 and USA
df2 = df[(df['Event distance/length'].isin(['50km', '50mi'])) & (df['Year of event'] == 2020) & (df['Event name'].str.split('(').str.get(1).str.split(')').str.get(0) == 'USA')]

# Event name without country name
df2['Event name'] = df2['Event name'].str.split('(').str.get(0)

# Athlete age
df2['Athlete age'] = 2020 - df2['Athlete year of birth']

# Time without final h
df2['Athlete performance'] = df2['Athlete performance'].str.split(' ').str.get(0)

# Drop colums: Athlete Club, Athlete Country, Athlete Year of birth, Athlete Age Category
df2 = df2.drop(['Athlete club', 'Athlete country', 'Athlete year of birth', 'Athlete age category'], axis = 1)

# Clean up null values
df2 = df2.dropna()

# Reset index
df2.reset_index(drop = True)

# Fix types
df2['Athlete age'] = df2['Athlete age'].astype(int)
df2['Athlete average speed'] = df2['Athlete average speed'].astype(float)

# Rename columns
df2 = df2.rename(columns = {'Year of event': 'year' ,
                            'Event dates': 'race_day' ,
                            'Event name': 'race_name',
                            'Event distance/length': 'race_length',
                            'Event number of finishers': 'race_number_of_finishers' ,
                            'Athlete performance': 'athlete_performance' ,
                            'Athlete gender': 'athlete_gender' ,
                            'Athlete average speed': 'athlete_average_speed' ,
                            'Athlete ID': 'athlete_id' ,
                            'Athlete age': 'athlete_age' })

# Reorder colums
df3 = df2[['race_day', 'race_name', 'race_length', 'race_number_of_finishers', 'athlete_id', 'athlete_gender', 'athlete_age', 'athlete_performance', 'athlete_average_speed']]
df3.head(10)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# QUESTIONS

# Difference in speed for the 50k, 50mi, male to female

q = """
SELECT race_length, athlete_gender, AVG(athlete_average_speed) as average_speed
FROM df2
GROUP BY race_length, athlete_gender
"""

df_q1 = pysqldf(q)
df_q1

# What age groups are the best in the 50m Race (20+ runners)

q = """
SELECT athlete_age, COUNT(athlete_id) as number_runners, AVG(athlete_average_speed) as average_speed
FROM df2
WHERE race_length = "50km"
GROUP BY athlete_age
HAVING number_runners > 20
ORDER BY average_speed DESC
LIMIT 10
"""

df_q2 = pysqldf(q)
df_q2

# What age groups are the worst in the 50m Race (20+ runners)

q = """
SELECT athlete_age, COUNT(athlete_id) as number_runners, AVG(athlete_average_speed) as average_speed
FROM df2
WHERE race_length = "50km"
GROUP BY athlete_age
HAVING number_runners > 20
ORDER BY average_speed
LIMIT 10
"""

df_q3 = pysqldf(q)
df_q3

# Number of runners in each season

# Spring 3-5
# Summer 6-8
# Fall 9-11
# Winter 12-2

q = """
SELECT 
    CASE 
        WHEN CAST(SUBSTR(race_day, INSTR(race_day, '.') + 1, INSTR(SUBSTR(race_day, INSTR(race_day, '.') + 1), '.') - 1) AS INTEGER) > 11 THEN 'Winter'
        WHEN CAST(SUBSTR(race_day, INSTR(race_day, '.') + 1, INSTR(SUBSTR(race_day, INSTR(race_day, '.') + 1), '.') - 1) AS INTEGER) > 8 THEN 'Fall'
        WHEN CAST(SUBSTR(race_day, INSTR(race_day, '.') + 1, INSTR(SUBSTR(race_day, INSTR(race_day, '.') + 1), '.') - 1) AS INTEGER) > 5 THEN 'Summer'
        WHEN CAST(SUBSTR(race_day, INSTR(race_day, '.') + 1, INSTR(SUBSTR(race_day, INSTR(race_day, '.') + 1), '.') - 1) AS INTEGER) > 2 THEN 'Spring'
        ELSE 'Winter'
    END AS race_season,
    COUNT(athlete_id) AS count
FROM df2
GROUP BY race_season
ORDER BY count DESC;
"""

df_q4 = pysqldf(q)
df_q4
