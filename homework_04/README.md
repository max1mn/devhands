# Задание 4

Latency-throughput диаграммы

## Статика

## Nginx

![статика nginx](raw/2024_04_06_11_41_00-http___localhost-c512_chart.png)

## Python (fastapi)

![статика python (fastapi)](raw/2024_04_06_12_29_41-http___localhost_python_fastapi_static-c64_chart.png)

## Go (vanilla net/http)

**Примечание:** без nginx forward-proxy

![статика go (vanilla)](raw/2024_04_07_10_01_55-http___localhost_8082_static-c256_chart.png)

## Нагрузка cpu 50ms

## Python (fastapi)

![cpu 50ms python (fastapi)](raw/2024_04_07_12_40_52-http___localhost_python_fastapi_payload_cpu_msec_50-c16_chart.png)

## Go (vanilla net/http)

![cpu 50ms go (vanilla)](raw/2024_04_07_13_08_04-http___localhost_go_vanilla_payload_cpu_msec_50-c16_chart.png)
