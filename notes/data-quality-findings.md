Data Quality Findings:


## 1. 
The data is for 1 city (Chicago); however, the data entries are free text with over 94 distinct locations within "City".



## 2.
Risk levels on establishments are stored as text without precedence ability. The risk level is an ordinal value and therefore cannot be stored as plain text.



## 3.
License # has only 19 true null values, but 831 rows carry a placeholder value of 0. These read as populated in a null count while carrying no identifying information. Because the re-inspection analysis partitions by license number, leaving these in would treat every affected row as belonging to one artificial establishment and produce meaningless results for all of them. They are coerced to null during cleaning. Among the 208 restaurant rows with a placeholder license, 51 of 192 categorized inspections were re-inspections, which implies a prior failed visit at the same establishment. Without a license number the two visits cannot be linked. Meaning the 51 visits are invisible to the analysis. These are routine canvasses and complaint responses at operating restaurants, not pre-license inspections, so the missing license number is a genuine data entry gap.



## 4.
Many results contain non-outcome statuses (Out of business, No Entry, Not Ready, Business Not Located) that must be excluded before computing the pass and fail rates, or every rating is understated.



## 5.
There are exactly the same amount of null values on Latitude, Longitude, and Location. This means that there is an issue with the geolocation and there are 1044 locations that are on this public data set, that aren't showing up. 



## 6.
Facility Type is uncontrolled free text with inconsistent casing and overlapping categories (CHURCH and CHURCH/SPECIAL EVENTS coexist as distinct values), so any aggregation by establishment type is approximate rather than exact. 

## 7.
-115,495 rows after filtering to 2020 onward, down from 315,223
-303 null licenses within that window, versus 831 placeholders across all years
-Risk 1 accounts for 79% of inspections, so the city's risk rating is heavily concentrated in one category
-Zero unparseable dates and zero duplicate Inspection IDs, both verified rather than assumed
-The city cleanup worked via substring matching rather than hand-mapping 90 variants-

## 8. Findings From SQL Query (1)
Within a facility type, the city's risk tier does predict failure rate in the expected direction. Restaurants fail at 23.0%, 21.4%, and 19.8% across Risk 1, 2, and 3. But the effect is small compared to variation between facility types: the lowest-risk liquor stores fail at 31.7%, above the highest-risk restaurants. Risk tier appears to encode the consequence of a failure rather than its likelihood.

## 9a. Findings From SQL Query (2)
Frequency is not severity. Code 55 (physical facilities installed, maintained, clean) is the most-cited violation in the dataset at 66,589 occurrences, but it does not appear in the top 15 by failure rate, meaning it shows up on passing inspections about as often as failing ones. Code 38 (insects, rodents, animals not present) is cited 19,094 times and appears on a failed inspection 67.3% of the time. Sorting by count would have surfaced the uninformative violation and hidden the predictive one.

## 9b. Findings From SQL Query (2)
Prior violation history predicts current failure, even after correction. Codes 59 and 60 ("PREVIOUS ... VIOLATION CORRECTED") are written when an establishment has fixed a violation flagged on an earlier visit. Inspections carrying code 59 are failures 91.4% of the time, and code 60 is 77.7%. Since these codes only appear where a violation history exists, they mark repeat offenders: the specific prior issue was corrected, but the establishment failed on other grounds. Tested whether this was an artifact of re-inspections and it was not, since routine Canvass visits account for the plurality of citations (3,813 of roughly 7,021).