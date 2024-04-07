# Задание 5

Latency-throughput диаграммы субд/кэш

## Go (vanilla net/http)

**Примечание:** без nginx forward-proxy

### 1 запрос к СУБД

![1 запрос к субд go (vanilla)](raw/2024_04_07_20_11_53-http___localhost_8082_db_count_1-c128_chart.png)

### 5 запросов к СУБД

![5 запросов к субд go (vanilla)](raw/2024_04_07_17_29_42-http___localhost_8082_db_count_5-c128_chart.png)

### 1 запрос к кэшу

![1 запрос к кэшу go (vanilla)](raw/2024_04_07_20_39_25-http___localhost_8082_cache_count_1-c256_chart.png)

### 5 запросов к кэшу

![5 запросов к кэшу go (vanilla)](raw/2024_04_07_18_11_59-http___localhost_8082_cache_count_5-c128_chart.png)
