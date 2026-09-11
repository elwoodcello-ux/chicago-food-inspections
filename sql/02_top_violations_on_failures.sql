-- Question: Which violations actually predict a failed inspection, as opposed
-- to which ones are merely common?
--
-- Joins the normalized violations table back to inspections. Sorting by rate
-- rather than frequency separates severity from prevalence: code 55 (physical
-- facilities maintained) is the most-cited violation in the dataset at 66,589
-- occurrences but does not appear in the top 15 by failure rate, meaning it
-- shows up on passing inspections about as often as failing ones.
--
-- Codes 59 and 60 ("PREVIOUS ... VIOLATION CORRECTED") mark establishments with
-- a prior violation history that has since been fixed. Their very high failure
-- rates (91.4% and 77.7%) therefore indicate repeat offenders failing on new
-- grounds rather than uncorrected issues. Checked for circularity with
-- re-inspections; routine Canvass visits are the plurality (3,813 of ~7,021).
--
-- Non-outcome statuses excluded. HAVING COUNT(*) >= 500 drops rare codes where
-- a high percentage would be noise.

SELECT
    v.violation_code,
    v.violation_desc,
    COUNT(*) AS times_cited,
    SUM(CASE WHEN i.results = 'Fail' THEN 1 ELSE 0 END) AS on_failures,
    ROUND(100.0 * SUM(CASE WHEN i.results = 'Fail' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_on_fail
FROM violations v
JOIN inspections i ON v.inspection_id = i.inspection_id
WHERE i.results IN ('Pass', 'Fail', 'Pass w/ Conditions')
GROUP BY v.violation_code, v.violation_desc
HAVING COUNT(*) >= 500
ORDER BY pct_on_fail DESC;