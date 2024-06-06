package handlers

import (
	"encoding/json"
	"net/http"
)

const (
	nanosecToMillisec = 1000 * 1000
)

type MessageResponse struct {
	Message string `json:"message"`
}

type TimingResponse struct {
	WallTimeMSec float64 `json:"wall_time_msec,omitepty"`
	TotalCycles  uint    `json:"total_cycles,omitepty"`
}

func JSONError(w http.ResponseWriter, err interface{}, code int) {
	writeJSONResponse(w, err, code)
}

func JSONResponse(w http.ResponseWriter, data interface{}) {
	writeJSONResponse(w, data, http.StatusOK)
}

func writeJSONResponse(w http.ResponseWriter, data interface{}, code int) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(data)
}
