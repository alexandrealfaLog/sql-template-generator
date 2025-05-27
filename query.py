sql_run = """
WITH RECURSIVE json_data AS (
    SELECT structure::json AS data
    FROM dataset_views
    WHERE dataset_id = $dataset_id
      AND "default" = TRUE
      AND id = $dataset_view_id
      AND dataset_id NOT IN ('13f89c0c-7f28-4b03-bc3a-07fe2f3c518a', '9d4ccdf5-6602-42f0-94b2-5734993f4124') -- datasets México
),
               flattened AS (
                   SELECT
                       jsonb_array_elements(data::jsonb) AS outer_element,
                       row_number() OVER () - 1 AS row_idx
                   FROM json_data
               ),
               more_flattened AS (
                   SELECT
                       jsonb_array_elements(f.outer_element) AS inner_element,
                       f.row_idx,
                       row_number() OVER (PARTITION BY f.row_idx) - 1 AS col_idx
                   FROM flattened f
               ),
               extra_flattened AS (
                   SELECT
                       e.element AS deepest_element,
                       mf.row_idx,
                       mf.col_idx
                   FROM more_flattened mf
                            CROSS JOIN LATERAL (
                       SELECT
                           CASE
                               WHEN jsonb_typeof(mf.inner_element) = 'array' THEN elem
                               ELSE mf.inner_element
                               END AS element
                       FROM jsonb_array_elements(
                                    CASE
                                        WHEN jsonb_typeof(mf.inner_element) = 'array' THEN mf.inner_element
                                        ELSE jsonb_build_array(mf.inner_element)
                                        END
                            ) AS arr(elem)
                       ) e
               ),
               extracted_values AS (
                   SELECT
                       (deepest_element->>'value')::int AS chart_value,
                       row_idx,
                       col_idx
                   FROM extra_flattened
                   WHERE deepest_element->>'type' = 'chart'
               ),
               chart_info AS (
                   SELECT
                       e.chart_value AS chart_id,
                       e.row_idx,
                       e.col_idx,
                       t.chart_type_id,
                       ct.component,
                       CASE
                           WHEN ct.component = 'resume-chart' THEN 'ResumeChart'
                           WHEN ct.component = 'line-chart' THEN 'LineChart'
                           WHEN ct.component = 'date-line-chart-v2' THEN 'DateLineChart'
                           WHEN ct.component = 'circle-chart' THEN 'CircleChart'
                           WHEN ct.component = 'annual-line-chart' THEN 'AnnualLineChart'
                           WHEN ct.component = 'Partitioned-bar-chart-AM' THEN 'PartitionedBarChartAm'
                           WHEN ct.component = 'barline-chart-am' THEN 'BarLineChart'
                           WHEN ct.component = 'route-chart' THEN 'RouteChart'
                           WHEN ct.component = 'board-chart-percentage' THEN 'BoardChartPercentage'
                           WHEN ct.component = 'general-chart' THEN 'GeneralChart'
                           WHEN ct.component = 'board-chart' THEN 'BoardChart'
                           ELSE ct.component
                           END AS chart_type_name
                   FROM extracted_values e
                            JOIN charts t ON t.id = e.chart_value
                            JOIN chart_types ct ON t.chart_type_id = ct.id
               ),
-- Adiciona altura individual de cada chart, seguindo as regras da lógica de grid
               chart_with_height AS (
                   SELECT *,
                          CASE
                              WHEN chart_type_name = 'ResumeChart' THEN 4
                              WHEN chart_type_name IN ('CircleChart', 'AnnualLineChart') THEN 2
                              ELSE 3
                              END AS h
                   FROM chart_info
               ),
-- Agora, definindo o valor de 'y' a partir da soma das alturas das linhas anteriores
               chart_with_y AS (
                   SELECT *,
                          COALESCE(
                                          SUM(h) OVER (
                                      ORDER BY row_idx
                                      ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                                      ), 0
                          ) AS y
                   FROM chart_with_height
               )
SELECT json_agg(
               json_build_object(
                       'grid',
                       (json_build_object(
                                'w', 6,
                                'x', CASE WHEN col_idx % 2 = 0 THEN 0 ELSE 6 END,
                                'y', y
                        )::jsonb
                           ||
                        CASE
                            WHEN chart_type_name NOT IN ('BoardChartPercentage', 'BoardChart', 'GeneralChart') THEN
                                json_build_object('h',
                                                  CASE
                                                      WHEN chart_type_name = 'ResumeChart' THEN 4
                                                      WHEN chart_type_name IN ('CircleChart', 'AnnualLineChart') THEN 2
                                                      ELSE 3
                                                      END
                                )::jsonb
                            ELSE '{}'::jsonb
                            END)::json,
                       'chart_id', chart_id::text,
                       'cellHeight', CASE
                                         WHEN chart_type_name IN ('GeneralChart', 'BoardChart', 'BoardChartPercentage') THEN '200px'
                                         WHEN chart_type_name IN ('CircleChart', 'AnnualLineChart') THEN '400px'
                                         ELSE '550px'
                           END,
                       'chart_type_name', chart_type_name
               )
               ORDER BY row_idx, col_idx
       ) AS formatted_structure
FROM chart_with_y;

"""

get_dataset_view_query = """
            SELECT id, dataset_id
            FROM dataset_views
            WHERE "default" = TRUE
              AND dataset_id NOT IN (
                             '13f89c0c-7f28-4b03-bc3a-07fe2f3c518a',
                             '9d4ccdf5-6602-42f0-94b2-5734993f4124'
                ) \
            """