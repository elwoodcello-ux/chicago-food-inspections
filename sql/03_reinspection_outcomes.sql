-- Question: When an establishment fails an inspection, does it pass the next
-- one, and how long does that take?
--
-- A window function is required here: LEAD() reaches forward to the next row
-- within each establishment's chronologically ordered inspection history. This
-- cannot be expressed with GROUP BY, which collapses the rows being compared.
--
-- The CTE exists because a window function cannot be referenced in WHERE, which
-- is evaluated before the window is computed. Computing it inside the CTE lets
-- the outer query filter on next_result.
--
-- Pass w/ Conditions is counted as a pass, consistent with query 01: the
-- establishment remained open. Rows with a null license are excluded, since
-- 831 placeholder zeros would otherwise merge unrelated establishments into a
-- single artificial history.
--
-- Result: 87.4% of failed establishments (21,714 of 22,178 failures had a
-- follow-up) passed their next inspection, at an average of 14.4 days. Broken
-- out by risk tier the recovery rate is flat (87.3 / 87.6 / 87.6), indicating
-- the city's risk tier does not predict compliance behavior.

WITH sequenced AS (
    SELECT
        license,
        risk_level,
        inspection_date,
        results,
        LEAD(results) OVER (PARTITION BY license ORDER BY inspection_date) AS next_result,
        LEAD(inspection_date) OVER (PARTITION BY license ORDER BY inspection_date) AS next_date
    FROM inspections
    WHERE license IS NOT NULL
      AND results IN ('Pass', 'Fail', 'Pass w/ Conditions')
)
SELECT
    risk_level,
    COUNT(*) AS failures_with_followup,
    SUM(CASE WHEN next_result IN ('Pass', 'Pass w/ Conditions') THEN 1 ELSE 0 END) AS passed_next,
    ROUND(100.0 * SUM(CASE WHEN next_result IN ('Pass', 'Pass w/ Conditions') THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_passed_next,
    ROUND(AVG(julianday(next_date) - julianday(inspection_date)), 1) AS avg_days_to_next
FROM sequenced
WHERE results = 'Fail'
  AND next_result IS NOT NULL
GROUP BY risk_level
ORDER BY risk_level;
