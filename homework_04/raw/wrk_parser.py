from dataclasses import dataclass, field
import json
import re
import sys
from collections import OrderedDict

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

PRINT_LATENCIES: dict[str, str] = OrderedDict(
    [
        # ("Max", "maxLatencies"),
        ("99%", "ninetyNinePercentileLatencies"),
        ("95%", "ninetyFivePercentileLatencies"),
        ("50%", "medianLatencies"),
        # ("Avg", "avgLatencies"),
    ]
)

PRINT_PLOTS: list[str] = [
    "latency",
    "errors",
    # "distribution",
    # "spectrum",
]

NUM_PLOTS = 3 + len(PRINT_PLOTS)


@dataclass
class LatencyResult:
    maxLatencies: list = field(default_factory=list)
    ninetyNinePercentileLatencies: list = field(default_factory=list)
    ninetyFivePercentileLatencies: list = field(default_factory=list)
    medianLatencies: list = field(default_factory=list)
    avgLatencies: list = field(default_factory=list)


def convert_to_kilobytes(value):
    unit_mapping = {
        "B": 1 / 1024,
        "KB": 1,
        "MB": 1024,
        "GB": 1024 * 1024,
        "TB": 1024 * 1024 * 1024,
    }

    unit = value[-2:]
    if unit in unit_mapping:
        val_str = value[:-2]  # Получаем числовую часть (исключая единицы измерения)
        val = float(val_str)
        return val * unit_mapping[unit]
    else:
        unit = value[-1]  # Если нет единиц времени, пробуем взять последний символ
        if unit in unit_mapping:
            val_str = value[:-1]
            val = float(val_str)
            return val * unit_mapping[unit]
        else:
            print("Unknown type:", unit)

    return None


def ms_to_human_readable(ms):
    if ms >= 1000 * 60 * 60:  # Если больше или равно 1 часу
        hours = round(ms / (1000 * 60 * 60), 1)
        return f"{hours:.2f}h"
    elif ms >= 1000 * 60:  # Если больше или равно 1 минуте
        minutes = round(ms / (1000 * 60), 1)
        return f"{minutes:.2f}m"
    elif ms >= 1000:  # Если больше или равно 1 секунде
        seconds = round(ms / 1000, 1)
        return f"{seconds:.2f}s"
    else:
        return f"{ms:.2f}ms"


def convert_to_ms(value):
    unit_mapping = {
        "us": 0.001,
        "μs": 0.001,
        "ms": 1,
        "s": 1000,
        "m": 60 * 1000,
        "h": 60 * 60 * 1000,
    }

    unit = value[-2:]
    if unit in unit_mapping:
        val_str = value[:-2]  # Получаем числовую часть (исключая единицы измерения)
        val = float(val_str)
        return val * unit_mapping[unit]
    else:
        unit = value[-1]  # Если нет единиц времени, пробуем взять последний символ
        if unit in unit_mapping:
            val_str = value[:-1]  # Получаем числовую часть (исключая единицы измерения)
            val = float(val_str)
            return val * unit_mapping[unit]
        else:
            print("Unknow time type:", unit)

    return None


def parse_wrk_output(output):
    data = {}

    # Поиск вызываемых настроек wrk
    wrk_command_match = re.search(r"wrk2 (.+)", output)
    if wrk_command_match:
        data["iteration_settings"] = {}
        wrk_command = wrk_command_match.group(1)
        # Извлечение параметров вызова
        params_match = re.findall(r"-([a-zA-Z])(\d+|\S+)", wrk_command)
        for param, value in params_match:
            data["iteration_settings"][param] = value

        # Поиск URL в строке
        urlResult = re.search(r"https?://\S+", wrk_command)
        if urlResult:
            data["iteration_settings"]["url"] = urlResult.group(0)

    # Поиск среднего времени ожидания
    latency_match = re.search(
        r"Latency\s+([0-9.]+[a-z]*)\s+([0-9.]+[a-z]*)\s+([0-9.]+[a-z]*)\s+([0-9.]+%)",
        output,
    )
    if latency_match:
        data["latency"] = {}
        data["latency"]["avg"] = latency_match.group(1)
        data["latency"]["stdev"] = latency_match.group(2)
        data["latency"]["max"] = latency_match.group(3)
        data["latency"]["stdev_percent"] = latency_match.group(4)

    # Поиск количества запросов в секунду
    req_sec_match = re.search(
        r"Req/Sec\s+([0-9.]+[a-z]*)\s+([0-9.]+[a-z]*)\s+([0-9.]+[a-z]*)\s+([0-9.]+%)",
        output,
    )
    if req_sec_match:
        data["req_per_sec"] = {}
        data["req_per_sec"]["avg"] = req_sec_match.group(1)
        data["req_per_sec"]["stdev"] = req_sec_match.group(2)
        data["req_per_sec"]["max"] = req_sec_match.group(3)
        data["req_per_sec"]["stdev_percent"] = req_sec_match.group(4)

    # Поиск данных о распределении задержек
    latency_distribution_match = re.search(
        r"Latency Distribution \(HdrHistogram - Recorded Latency HDR\)\n([\s\S]+?)(?:Detailed)",
        output,
    )
    if latency_distribution_match:
        latency_distribution_lines = latency_distribution_match.group(1).split("\n")
        data["latency_distribution"] = {}
        for line in latency_distribution_lines:
            if line.strip().startswith("Percentile"):
                continue
            parts = line.strip().split()
            if len(parts) == 2:
                percentile, latency = parts
                data["latency_distribution"][percentile] = latency

    # Поиск данных о спектре процентилей
    percentile_spectrum_match = re.search(
        r"Detailed Percentile Spectrum:\n([\s\S]+?)(?:#\[\S+)", output
    )
    if percentile_spectrum_match:
        percentile_spectrum_lines = percentile_spectrum_match.group(1).split("\n")
        data["percentile_spectrum"] = {}
        for line in percentile_spectrum_lines:
            if line.strip().startswith("Value"):
                continue
            if line.startswith("#"):
                break
            parts = line.strip().split()
            if len(parts) == 4:
                value, percentile, total_count, one_by_one_minus_percentile = parts
                data["percentile_spectrum"][percentile] = {
                    "value": value,
                    "total_count": total_count,
                    "percentile_normalization_coefficient": one_by_one_minus_percentile,
                }

    data["total"] = {}
    # Поиск количества запросов и ошибок сокета
    req_match = re.search(
        r"(\d+) requests in ([0-9.]+[a-z]*), ([0-9.]+[a-zA-Z]*) read", output
    )
    if req_match:
        data["total"]["requests"] = req_match.group(1)
        data["total"]["time"] = req_match.group(2)
        data["total"]["data_read"] = req_match.group(3)

    # Поиск количества запросов в секунду
    req_sec_match = re.search(r"Requests/sec:\s+([\d.]+)", output)
    if req_sec_match:
        data["total"]["requests_per_sec"] = req_sec_match.group(1)

    # Поиск передачи данных в секунду
    transfer_sec_match = re.search(r"Transfer/sec:\s+([\d.]+[a-zA-Z]+)", output)
    if transfer_sec_match:
        data["total"]["transfer_per_sec"] = transfer_sec_match.group(1)

    data["errors"] = {
        "socket_connect": 0,
        "socket_read": 0,
        "socket_write": 0,
        "socket_timeout": 0,
        "non_2xx_or_3xx_response": 0,
    }
    # Поиск ошибок сокета
    socket_errors_match = re.search(
        r"Socket errors: connect (\d+), read (\d+), write (\d+), timeout (\d+)", output
    )
    if socket_errors_match:
        data["errors"]["socket_connect"] = int(socket_errors_match.group(1))
        data["errors"]["socket_read"] = int(socket_errors_match.group(2))
        data["errors"]["socket_write"] = int(socket_errors_match.group(3))
        data["errors"]["socket_timeout"] = int(socket_errors_match.group(4))
    response_errors_match = re.search(r"Non-2xx or 3xx responses: (\d+)", output)
    if response_errors_match:
        data["errors"]["non_2xx_or_3xx_response"] = int(response_errors_match.group(1))

    return data


def parse_wrk_results(file_content):
    # Разбиваем содержимое файла на результаты работы wrk
    results = re.split(r"[-—]+(?:\n|\r\n)wrk2", file_content)
    parsed_results = []
    for result in results:
        if result.strip() == "":
            continue
        result = "wrk2" + result
        parsed_result = parse_wrk_output(result)
        parsed_results.append(parsed_result)
    return parsed_results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python wrk_parser.py <input_filename.txt>")
        sys.exit(1)

    input_filename = sys.argv[1]
    with open(input_filename, "r") as file:
        input_data = file.read()

    parsed_results = parse_wrk_results(input_data)

    # Запись результатов парсинга в новый файл
    output_filename = f"{input_filename[:-4]}_parsed.json"
    with open(output_filename, "w") as file:
        file.write(json.dumps(parsed_results))

    print(f"Parsed results saved to {output_filename}")

    fig = plt.figure(figsize=(13, 26 / 7 * NUM_PLOTS))
    gs = GridSpec(
        NUM_PLOTS,
        2,
        figure=fig,
        top=0.97,
        bottom=0.03,
        left=0.07,
        right=0.93,
        hspace=0.4,
        wspace=0.2,
        height_ratios=[0.5, 1, 1, 0.5, 0.8, 2, 2][:NUM_PLOTS],
        width_ratios=[1, 1],
    )

    ax0 = fig.add_subplot(gs[0, 0])
    localizations = {
        "t": "Threads",
        "c": "Connections",
        "R": "Requested RPS",
        "d": "Test iteration durations",
        "url": "URL",
    }
    table_data = []
    table_data.append(["Tests count", len(parsed_results)])
    for key in parsed_results[0]["iteration_settings"].keys():
        values = [elem["iteration_settings"][key] for elem in parsed_results]
        unique_values = set(values)
        if len(unique_values) == 1:
            table_data.append([localizations.get(key, key), values[0]])
        else:
            table_data.append(
                [localizations.get(key, key), f"{min(values)}-{max(values)}"]
            )

    table = ax0.table(cellText=table_data, loc="center", cellLoc="left")
    ax0.axis("off")
    table.scale(1, 1.6)

    rs = [int(item["iteration_settings"]["R"]) for item in parsed_results]

    ax1 = fig.add_subplot(gs[1, 0])
    RPSs = [float(item["total"]["requests_per_sec"]) for item in parsed_results]
    ax1.plot(rs, RPSs, label="Real", marker="o")
    ax1.plot(rs, rs, label="Requested", marker="o")
    ax1.set_title("RPS")
    ax1.set_xlabel("R=")
    ax1.legend()
    ax1.grid(True)

    ax2 = fig.add_subplot(gs[1, 1])
    requestsReal = [
        convert_to_kilobytes(item["total"]["transfer_per_sec"])
        for item in parsed_results
    ]
    ax2.plot(rs, requestsReal, label="Transfer/sec", marker="o")
    ax2.set_title("Transfer/sec (KB)")
    ax2.set_xlabel("R=")
    ax2.grid(True)

    def getPercentileLatency(targetPercentile):
        targetPercentileLatencies = []
        for item in parsed_results:
            closestPercentile = "0"
            for percentile in item["percentile_spectrum"].keys():
                if abs(targetPercentile / 100 - float(percentile)) < abs(
                    targetPercentile / 100 - float(closestPercentile)
                ):
                    closestPercentile = percentile
            targetPercentileLatencies.append(
                float(item["percentile_spectrum"][closestPercentile]["value"])
            )
        return targetPercentileLatencies

    latencies = LatencyResult()
    latencies.ninetyFivePercentileLatencies = getPercentileLatency(95)
    latencies.ninetyNinePercentileLatencies = getPercentileLatency(99)
    latencies.avgLatencies = [
        convert_to_ms(item["latency"]["avg"]) for item in parsed_results
    ]
    latencies.medianLatencies = [
        convert_to_ms(item["latency_distribution"]["50.000%"])
        for item in parsed_results
    ]
    latencies.maxLatencies = [
        convert_to_ms(item["latency"]["max"]) for item in parsed_results
    ]

    if "latency" in PRINT_PLOTS:
        ax3 = fig.add_subplot(gs[2, :])
        for label, attr in PRINT_LATENCIES.items():
            ax3.plot(rs, getattr(latencies, attr), label=label, marker="o")

        ax3.set_title("Latency (ms)")
        ax3.legend()
        ax3.set_xlabel("R=")
        ax3.grid(True)

    socket_connect_errors = [
        item["errors"]["socket_connect"] for item in parsed_results
    ]
    socket_read_errors = [item["errors"]["socket_read"] for item in parsed_results]
    socket_write_errors = [item["errors"]["socket_write"] for item in parsed_results]
    socket_timeout_errors = [
        item["errors"]["socket_timeout"] for item in parsed_results
    ]
    non_2xx_or_3xx_response_errors = [
        item["errors"]["non_2xx_or_3xx_response"] for item in parsed_results
    ]

    if "errors" in PRINT_PLOTS:
        ax4 = fig.add_subplot(gs[3, :])
        ax4.plot(rs, socket_connect_errors, label="SocketConnect Errors", marker="o")
        ax4.plot(rs, socket_read_errors, label="SocketRead Errors", marker="o")
        ax4.plot(rs, socket_write_errors, label="SocketWrite Errors", marker="o")
        ax4.plot(rs, socket_timeout_errors, label="SocketTimeout Errors", marker="o")
        ax4.plot(
            rs,
            non_2xx_or_3xx_response_errors,
            label="non-2xx/3xx responses",
            marker="o",
        )
        ax4.set_title("Errors count")
        ax4.set_xlabel("R=")
        ax4.legend()
        ax4.grid(True)

    table_data = [[], [], [], [], [], [], [], [], []]
    table_data[0] = rs.copy()
    table_data[0].insert(0, "R=")
    table_data[1] = [
        int(float(elem["total"]["requests_per_sec"])) for elem in parsed_results
    ]
    table_data[1].insert(0, "RPS")
    table_data[2] = [item["total"]["transfer_per_sec"] for item in parsed_results]
    table_data[2].insert(0, "Tran/sec")
    table_data[3] = [elem["latency"]["avg"] for elem in parsed_results]
    table_data[3].insert(0, "Avg lat")
    table_data[4] = [elem["latency_distribution"]["50.000%"] for elem in parsed_results]
    table_data[4].insert(0, "50% lat")
    table_data[5] = [
        ms_to_human_readable(elem)
        for elem in latencies.ninetyFivePercentileLatencies.copy()
    ]
    table_data[5].insert(0, "95% lat")
    table_data[6] = [
        ms_to_human_readable(elem)
        for elem in latencies.ninetyNinePercentileLatencies.copy()
    ]
    table_data[6].insert(0, "99% lat")
    table_data[7] = [elem["latency"]["max"] for elem in parsed_results]
    table_data[7].insert(0, "Max lat")
    table_data[8] = [sum(item["errors"].values()) for item in parsed_results]
    table_data[8].insert(0, "Errors")
    ax01 = fig.add_subplot(gs[4, :])
    ax01.axis("off")
    table = ax01.table(cellText=table_data, loc="center", cellLoc="left")
    table.scale(1, 1.4)

    if "distribution" in PRINT_PLOTS:
        ax5 = fig.add_subplot(gs[5, :])
        inner_ax1 = ax5
        for item in parsed_results:
            percentiles = list(item["latency_distribution"].keys())
            latency_values = [
                convert_to_ms(item["latency_distribution"][p]) for p in percentiles
            ]
            percentiles = [float(p[:-1]) for p in percentiles]
            inner_ax1.plot(
                percentiles,
                latency_values,
                label=f'R={item["iteration_settings"]["R"]}',
                marker="o",
            )

        inner_ax1.set_title("Latency (ms) distribution")
        inner_ax1.set_xlabel("Percentile")
        inner_ax1.legend()
        inner_ax1.grid(True)

    if "spectrum" in PRINT_PLOTS:
        ax5 = fig.add_subplot(gs[6, :])
        inner_ax2 = ax5
        for item in parsed_results:
            percentiles = list(item["percentile_spectrum"].keys())
            latency_values = [
                float(item["percentile_spectrum"][p]["value"]) for p in percentiles
            ]
            percentiles = [100 * float(p) for p in percentiles]
            inner_ax2.plot(
                percentiles,
                latency_values,
                label=f'R={item["iteration_settings"]["R"]}',
            )

        inner_ax2.set_title("Latency (ms) percentile spectrum")
        inner_ax2.set_xlabel("Percentile")
        inner_ax2.legend()
        inner_ax2.grid(True)

    chart_filename = f"{input_filename[:-4]}_chart.png"
    plt.savefig(chart_filename)
    print(f"Chart saved to {chart_filename}")
