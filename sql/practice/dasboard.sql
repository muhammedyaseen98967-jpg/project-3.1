
--CARD 1 — Bowlers in Data
SELECT
    COUNT(*) AS total_bowlers,

    SUM(
        CASE
            WHEN balls >= 300 THEN 1
            ELSE 0
        END
    ) AS qualifying_bowlers

FROM
(
    SELECT
        bowler,
        SUM(is_legal) AS balls

    FROM v_ball

    GROUP BY bowler
);


--CARD 2 — Credited Wickets
SELECT
    SUM(bowler_wicket) AS total_wickets

FROM v_ball;


--CARD 3 — Spin vs Pace Economy
SELECT
    CASE
        WHEN bowler_type LIKE '%Legbreak%'
          OR bowler_type LIKE '%Offbreak%'
          OR bowler_type LIKE '%Orthodox%'
          OR bowler_type LIKE '%Googly%'
          OR bowler_type LIKE '%Wrist spin%'
        THEN 'Spin'
        ELSE 'Pace'
    END AS style,

    SUM(is_legal) AS balls,

    ROUND(
        6.0 * SUM(bowler_runs)
        / SUM(is_legal),
        2
    ) AS economy,

    ROUND(
        100.0 * SUM(bowler_wicket)
        / SUM(is_legal),
        2
    ) AS wicket_pct

FROM v_ball

WHERE
    TRIM(COALESCE(bowler_type,'')) <> ''

GROUP BY style;

--HERO CHART — Economy by Phase: Spin vs Pace

SELECT
    phase,

    CASE
        WHEN bowler_type LIKE '%Legbreak%'
          OR bowler_type LIKE '%Offbreak%'
          OR bowler_type LIKE '%Orthodox%'
          OR bowler_type LIKE '%Googly%'
          OR bowler_type LIKE '%Wrist spin%'
        THEN 'Spin'
        ELSE 'Pace'
    END AS style,

    ROUND(
        6.0 * SUM(bowler_runs)
        / SUM(is_legal),
        2
    ) AS economy

FROM v_ball

WHERE
    TRIM(COALESCE(bowler_type,'')) <> ''

GROUP BY
    phase,
    style

ORDER BY
    phase,
    style;

    --SUPPORTING CHART — Bowling Styles Economy
SELECT
    bowler_type,

    SUM(is_legal) AS balls,

    ROUND(
        6.0 * SUM(bowler_runs)
        / SUM(is_legal),
        2
    ) AS economy

FROM v_ball

WHERE
    TRIM(COALESCE(bowler_type,'')) <> ''

GROUP BY
    bowler_type

HAVING
    balls >= 3000

ORDER BY
    economy ASC

LIMIT 5;

--CONTEXT CHART — Wickets by Phase
SELECT
    phase,

    SUM(bowler_wicket) AS wickets,

    SUM(is_legal) AS balls

FROM v_ball

GROUP BY phase

ORDER BY
    CASE phase
        WHEN 'Powerplay' THEN 1
        WHEN 'Middle' THEN 2
        WHEN 'Death' THEN 3
    END;



    --CONTEXT CHART — Dot-ball Share: Spin vs Pace
SELECT
    CASE
        WHEN bowler_type LIKE '%Legbreak%'
          OR bowler_type LIKE '%Offbreak%'
          OR bowler_type LIKE '%Orthodox%'
          OR bowler_type LIKE '%Googly%'
          OR bowler_type LIKE '%Wrist spin%'
        THEN 'Spin'
        ELSE 'Pace'
    END AS style,

    SUM(is_legal) AS balls,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN batter_runs = 0
                     AND is_legal = 1
                THEN 1
                ELSE 0
            END
        )
        / SUM(is_legal),
        2
    ) AS dot_pct

FROM v_ball

WHERE
    TRIM(COALESCE(bowler_type,'')) <> ''

GROUP BY style;
--
