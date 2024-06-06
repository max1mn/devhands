package payload

import (
	"time"
)

type dummyPayload struct {
}

func NewDummyPayload() dummyPayload {
	return dummyPayload{}
}

func (p dummyPayload) Sleep(msec float64) (uint, error) {
	var cycles uint

	timeNow := time.Now().Local()
	interval := time.Duration(msec * float64(time.Millisecond))

	for time.Since(timeNow) < interval {
		pr := 213123.0
		pr *= pr
		pr = +1

		cycles++
	}
	return cycles, nil
}
