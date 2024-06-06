import typing
import hashlib
import resource
import time
import asyncio

from fastapi import APIRouter

_DATA = open("/dev/urandom","rb").read(1024)
_CPU_JOB = lambda: hashlib.md5(_DATA)

router = APIRouter()

SWITCH_CONTEXT_CPU_JOB_CYCLES: int = 32

async def u_sleep_getrusage(msec: float, _: typing.Callable) -> None:
    """Вариант без переключения контекста asyncio (getrusage)"""
    total_time: float = 0
    cycle_count: int = 0

    start_usage = resource.getrusage(resource.RUSAGE_THREAD)
    while total_time < msec / 1000:
        _CPU_JOB()
        cycle_count += 1

        if cycle_count >= SWITCH_CONTEXT_CPU_JOB_CYCLES:
            end_usage = resource.getrusage(resource.RUSAGE_THREAD)
            total_time += end_usage.ru_utime - start_usage.ru_utime
            total_time += end_usage.ru_stime - start_usage.ru_stime

            cycle_count = 0
            start_usage = end_usage


async def u_sleep_getrusage_switch(msec: float, switch_counter: typing.Callable) -> None:
    """Вариант с переключением контекста asyncio (getrusage)"""
    total_time: float = 0
    cycle_count: int = 0

    start_usage = resource.getrusage(resource.RUSAGE_THREAD)
    while total_time < msec / 1000:
        _CPU_JOB()
        cycle_count += 1

        if cycle_count >= SWITCH_CONTEXT_CPU_JOB_CYCLES:
            end_usage = resource.getrusage(resource.RUSAGE_THREAD)
            total_time += end_usage.ru_utime - start_usage.ru_utime
            total_time += end_usage.ru_stime - start_usage.ru_stime

            # asyncio context switch
            switch_counter()
            await asyncio.sleep(0)

            # start cycle
            cycle_count = 0
            start_usage = resource.getrusage(resource.RUSAGE_THREAD)

async def u_sleep_clock_switch(msec: float, switch_counter: typing.Callable):
    """Вариант с переключением контекста asyncio (perf_counter)"""
    total_time: float = 0
    cycle_count: int = 0

    start_clock = time.perf_counter()
    while total_time < msec / 1000:
        _CPU_JOB()
        cycle_count += 1

        if cycle_count >= SWITCH_CONTEXT_CPU_JOB_CYCLES:
            total_time += time.perf_counter() - start_clock

            # context switch
            switch_counter()
            await asyncio.sleep(0)

            # start cycle
            cycle_count = 0
            start_clock = time.perf_counter()


async def io_sleep(msec: float, switch_counter: typing.Callable) -> None:
    await asyncio.sleep(msec / 1000)
    switch_counter()

u_sleep = u_sleep_getrusage

@router.get("")
async def get_root(cpu_msec: float = 0, io_msec: float = 0):
    start = time.perf_counter()

    switch_count: int = 0
    def switch_counter():
        nonlocal switch_count
        switch_count += 1

    if cpu_msec:
        await u_sleep(cpu_msec, switch_counter)

    if io_msec:
        await io_sleep(io_msec, switch_counter)

    end = time.perf_counter()

    return {"wall_time_msec": 1000 * (end - start), "context_switches": switch_count}
