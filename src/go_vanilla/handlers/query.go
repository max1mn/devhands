package handlers

import (
	"context"
	"errors"
	"net/http"
	"strconv"
	"time"

	"go.uber.org/zap"
)

type QueryPayload interface {
	Query(ctx context.Context, count uint) error
	Close() error
}

func QueryHandler(dbPayload QueryPayload) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		// count
		countStr := r.URL.Query().Get("count")
		if countStr == "" {
			JSONError(w, errors.New("count not specified"), http.StatusBadRequest)
			return
		}
		count, err := strconv.ParseUint(countStr, 10, 0)
		if err != nil {
			JSONError(w, err, http.StatusBadRequest)
			return
		}

		err = dbPayload.Query(r.Context(), uint(count))
		if err != nil {
			zap.L().Error("storage error", zap.Error(err))
			JSONError(w, err, http.StatusInternalServerError)
			return
		}

		// wall time
		end := time.Now()

		JSONResponse(w, TimingResponse{
			WallTimeMSec: float64(end.Sub(start).Nanoseconds()) / nanosecToMillisec,
		})
	}
}
