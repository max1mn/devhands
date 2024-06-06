package main

import (
	"flag"
	"fmt"
	"net/http"
	"runtime"

	"github.com/max1mn/devhands_go_vanilla/handlers"
	"github.com/max1mn/devhands_go_vanilla/payload"
	"go.uber.org/zap"
)

var (
	host string
	port int
)

func init() {
	flag.StringVar(&host, "host", "", "server host")
	flag.IntVar(&port, "port", 8082, "server port")
}

func main() {
	runtime.GOMAXPROCS(2 * runtime.NumCPU())

	logger := zap.NewExample()
	defer logger.Sync()

	undo := zap.ReplaceGlobals(logger)
	defer undo()

	flag.Parse()

	http.HandleFunc("/", handlers.Ok)
	http.HandleFunc("/static", handlers.Static)

	// sleeps
	cpuSleep := payload.NewGetrusagePayload()
	ioSleep := payload.NewIOPayload()
	http.HandleFunc("/payload", handlers.SleepHandler(cpuSleep, ioSleep))

	// mysql
	mysqlQuery := payload.NewMysqlPayload()
	defer mysqlQuery.Close()

	http.HandleFunc("/db", handlers.QueryHandler(mysqlQuery))

	// redis
	redisQuery := payload.NewRedisPayload()
	defer redisQuery.Close()

	http.HandleFunc("/cache", handlers.QueryHandler(redisQuery))

	addr := fmt.Sprintf("%s:%d", host, port)
	fmt.Println("serving at " + addr)
	http.ListenAndServe(addr, nil)

}
