package handlers

import (
	"net/http"
	"strconv"
	"time"

	"go.uber.org/zap"
)

type SleepPayload interface {
	Sleep(msec float64) (uint, error)
}

func SleepHandler(cpuPayload SleepPayload, ioPayload SleepPayload) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		var totalCycles uint

		// cpu sleep
		if cpuMsecStr := r.URL.Query().Get("cpu_msec"); cpuMsecStr != "" {
			msec, err := strconv.ParseFloat(cpuMsecStr, 32)
			if err != nil {
				JSONError(w, err, http.StatusBadRequest)
				return
			}

			cycles, err := cpuPayload.Sleep(msec)
			if err != nil {
				zap.L().Error("cpu sleep error", zap.Error(err))
				JSONError(w, err, http.StatusInternalServerError)
				return
			}
			totalCycles += cycles
		}

		// io sleep
		if ioMsecStr := r.URL.Query().Get("io_msec"); ioMsecStr != "" {
			msec, err := strconv.ParseFloat(ioMsecStr, 32)
			if err != nil {
				JSONError(w, err, http.StatusBadRequest)
				return
			}

			cycles, err := ioPayload.Sleep(msec)
			if err != nil {
				zap.L().Error("io sleep error", zap.Error(err))
				JSONError(w, err, http.StatusInternalServerError)
				return
			}
			totalCycles += cycles
		}

		end := time.Now()

		JSONResponse(w, TimingResponse{
			WallTimeMSec: float64(end.Sub(start).Nanoseconds()) / nanosecToMillisec,
			TotalCycles:  totalCycles,
		})
	}
}
