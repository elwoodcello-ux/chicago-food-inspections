The 5 dirty findings in the data:

1.
The data is for 1 city (Chicago); however, the data entries are free text with over 94 distinct locations within "City".



2.
Risk levels on violations are stored as text without precedence ability. The risk level is an ordinal value and therefore cannot be stored as plain text.



3.
There are 19 null License numbers which is risky. A null is an unknown and can mess up other data points and insights. 



4.
There are many instances in the results category that contribute to the number of passes; however, there are many entries that there was no inspection done, such as, Out of business, No entry, Not Ready, or Business Not Located. 



5.
There are exactly the same amount of null values on Latitude, Longitude, and Location. This means that there is an issue with the geolocation and there are 1044 locations that are on this public data set, that aren't showing up. 