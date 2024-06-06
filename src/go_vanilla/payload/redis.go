package payload

import (
	"context"
	"fmt"

	"github.com/redis/go-redis/v9"
)

type redisPayload struct {
	client *redis.Client
}

func NewRedisPayload() *redisPayload {
	client := redis.NewClient(&redis.Options{
		Addr:     "localhost:6379",
		Password: "", // no password set
		DB:       0,  // use default DB
	})

	return &redisPayload{
		client: client,
	}
}

func (p *redisPayload) Close() error {
	return p.client.Close()
}

func (p *redisPayload) Query(ctx context.Context, count uint) error {
	for i := uint(0); i < count; i++ {
		_, err := p.client.Get(ctx, fmt.Sprintf("user:%d", randomUserID())).Result()
		if err != nil {
			return err
		}
	}

	return nil
}
