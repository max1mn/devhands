# Задание 3

Ручки для тестирования нагрузки

## Python (fastapi)

### Запуск

```shell
wrk2 -c64 -t4 -d30s -R1000 -L http://localhost/python_fastapi/payload?cpu_msec=10
```

### Результат

x8 workers max ~650 rps

### Код

```python
import typing
import hashlib
import resource
import time
import asyncio

from fastapi import APIRouter

_PROFILE_JOB_CYCLES = 32

_DATA = open("/dev/urandom","rb").read(1024)
_CPU_JOB = lambda: hashlib.md5(_DATA)

router = APIRouter()

async def u_sleep(msec: float) -> None:
    total_time: float = 0
    cycle_count: int = 0

    start_usage = resource.getrusage(resource.RUSAGE_THREAD)
    while total_time < msec / 1000:
        _CPU_JOB()
        cycle_count += 1

        if cycle_count >= _PROFILE_JOB_CYCLES:
            end_usage = resource.getrusage(resource.RUSAGE_THREAD)
            total_time += end_usage.ru_utime - start_usage.ru_utime
            total_time += end_usage.ru_stime - start_usage.ru_stime

            cycle_count = 0
            start_usage = end_usage


async def io_sleep(msec: float) -> None:
    await asyncio.sleep(msec / 1000)

@router.get("")
async def get_root(cpu_msec: float = 0, io_msec: float = 0):
    start = time.perf_counter()

    if cpu_msec:
        await u_sleep(cpu_msec)

    if io_msec:
        await io_sleep(io_msec)

    end = time.perf_counter()

    return {"wall_time_msec": 1000 * (end - start)}
```

## Go (vanilla net/http)

### Запуск

```shell
wrk2 -c64 -t4 -d30s -R1000 -L http://localhost/go_vanilla/payload?cpu_msec=10
```

### Результат

при `runtime.GOMAXPROCS(2 * runtime.NumCPU())` max ~610 rps

### Код

```golang
package handlers

import (
    "crypto/md5"
    "net/http"
    "os"
    "runtime"
    "strconv"
    "syscall"
    "time"

    "go.uber.org/zap"
)

type TimingResponse struct {
    WallTimeMSec float64 `json:"wall_time_msec"`
}

const (
    profileJobCycles  = 32
    nanosecToMillisec = 1_000_000
)

var (
    data []byte
)

func init() {
    file, err := os.Open("/dev/urandom")
    if err != nil {
        panic(err)
    }
    defer file.Close()

    data = make([]byte, 1024)
    file.Read(data)
}

func job() {
    _ = md5.Sum(data)
}

func cpuSleep(msec float64) error {
    runtime.LockOSThread()
    defer runtime.UnlockOSThread()

    var totalTime float64
    var cyclesCount int

    startUsage := syscall.Rusage{}
    if err := syscall.Getrusage(syscall.RUSAGE_THREAD, &startUsage); err != nil {
        zap.L().Error("getrusage error", zap.Error(err))
        return err
    }

    endUsage := syscall.Rusage{}
    for totalTime < msec {
        job()
        cyclesCount++

        if cyclesCount >= profileJobCycles {
            if err := syscall.Getrusage(syscall.RUSAGE_THREAD, &endUsage); err != nil {
                zap.L().Error("getrusage error", zap.Error(err))
                return err
            }

            totalTime += (float64(endUsage.Utime.Nano()) - float64(startUsage.Utime.Nano())) / nanosecToMillisec
            totalTime += (float64(endUsage.Stime.Nano()) - float64(startUsage.Stime.Nano())) / nanosecToMillisec

            startUsage.Utime = endUsage.Utime
            startUsage.Stime = endUsage.Stime

            cyclesCount = 0
        }
    }

    return nil
}

func ioSleep(msec float64) error {
    time.Sleep(time.Duration(msec * float64(time.Millisecond)))
    return nil
}

func Payload(w http.ResponseWriter, r *http.Request) {
    start := time.Now()

    if cpuMsecStr := r.URL.Query().Get("cpu_msec"); cpuMsecStr != "" {
        msec, err := strconv.ParseFloat(cpuMsecStr, 32)
        if err != nil {
            JSONError(w, err, http.StatusBadRequest)
            return
        }

        cpuSleep(msec)
    }

    if ioMsecStr := r.URL.Query().Get("io_msec"); ioMsecStr != "" {
        msec, err := strconv.ParseFloat(ioMsecStr, 32)
        if err != nil {
            JSONError(w, err, http.StatusBadRequest)
            return
        }

        ioSleep(msec)
    }

    end := time.Now()

    JSONResponse(w, TimingResponse{float64(end.Sub(start).Nanoseconds()) / nanosecToMillisec})
}

```
