package payload

import (
	"fmt"
	"os"
	"runtime"
	"syscall"

	"go.uber.org/zap"
)

const (
	bufSize = 64 * 1024 // 64 kb
)

type getrusagePayload struct {
	data []byte
}

func NewGetrusagePayload() getrusagePayload {
	file, err := os.Open("/dev/urandom")
	if err != nil {
		panic(err)
	}
	defer file.Close()

	data := make([]byte, bufSize)
	file.Read(data)

	fmt.Println(data)

	return getrusagePayload{
		data: data,
	}
}

func elapsedUsageMsec(startUsage syscall.Rusage) (float64, error) {
	usage := syscall.Rusage{}
	if err := syscall.Getrusage(syscall.RUSAGE_THREAD, &usage); err != nil {
		zap.L().Error("getrusage error", zap.Error(err))
		return 0, err
	}

	elapsed := float64(usage.Utime.Nano()) - float64(startUsage.Utime.Nano()) +
		float64(usage.Stime.Nano()) - float64(startUsage.Stime.Nano())
	elapsed /= nanosecToMillisec

	return elapsed, nil
}

func (p getrusagePayload) Sleep(msec float64) (uint, error) {
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()

	var elapsedMsec float64
	var cycles uint

	startUsage := syscall.Rusage{}
	if err := syscall.Getrusage(syscall.RUSAGE_THREAD, &startUsage); err != nil {
		zap.L().Error("getrusage error", zap.Error(err))
		return 0, err
	}

	var err error
	for elapsedMsec < msec {
		md5Work(p.data)

		cycles++
		if elapsedMsec, err = elapsedUsageMsec(startUsage); err != nil {
			return 0, err
		}
	}

	return cycles, nil
}
