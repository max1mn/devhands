package payload

import "time"

type ioPayload struct {
}

func NewIOPayload() ioPayload {
	return ioPayload{}
}

func (p ioPayload) Sleep(msec float64) (uint, error) {
	time.Sleep(time.Duration(msec * float64(time.Millisecond)))
	return 0, nil
}
