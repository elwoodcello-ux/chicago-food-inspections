-- Question: Which facility types fail inspections most often, and does the
-- city's pre-assigned risk tier predict failure?
--
-- Non-outcome statuses (Out of Business, No Entry, Not Ready, Business Not
-- Located) are excluded: 18,765 of 115,495 rows, 16% of the data. Leaving
-- them in the denominator understates every failure rate.
--
-- HAVING COUNT(*) >= 200 drops groups too small to be meaningful.

SELECT
    facility_type,
    risk_level,
    COUNT(*) AS total,
    SUM(CASE WHEN results = 'Fail' THEN 1 ELSE 0 END) AS failures,
    ROUND(100.0 * SUM(CASE WHEN results = 'Fail' THEN 1 ELSE 0 END) / COUNT(*), 1) AS fail_pct
FROM inspections
WHERE results IN ('Pass', 'Fail', 'Pass w/ Conditions')
GROUP BY facility_type, risk_level
HAVING COUNT(*) >= 200
ORDER BY fail_pct DESC;
