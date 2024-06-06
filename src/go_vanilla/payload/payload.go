package payload

import (
	"crypto/md5"
	"math/rand"
)

const (
	nanosecToMillisec = 1000 * 1000
)

func randomUserID() uint {
	return uint(1 + rand.Intn(1000))
}
func md5Work(data []byte) {
	_ = md5.Sum(data)
}
