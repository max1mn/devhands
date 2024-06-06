package payload

import (
	"context"
	"fmt"

	"database/sql"

	_ "github.com/go-sql-driver/mysql"
)

type mysqlPayload struct {
	db *sql.DB
}

func NewMysqlPayload() *mysqlPayload {
	db, err := sql.Open("mysql", "root@tcp(127.0.0.1:3306)/devhands")
	if err != nil {
		panic(err)
	}

	db.SetMaxOpenConns(100)

	return &mysqlPayload{
		db: db,
	}
}

func (p *mysqlPayload) Close() error {
	return p.db.Close()
}

func (p *mysqlPayload) Query(ctx context.Context, count uint) error {
	for i := uint(0); i < count; i++ {
		_, err := p.db.ExecContext(ctx, fmt.Sprintf("SELECT * FROM users WHERE id = %d", randomUserID()))
		if err != nil {
			return err
		}
	}

	return nil
}
