package database

import (
	"database/sql"
	"log"
	
	_ "github.com/mattn/go-sqlite3"
	"backend/internal/config"
)

func InitDB(cfg *config.Config) *sql.DB {
	db, err := sql.Open("sqlite3", "tasks.db")
	if err != nil {
		log.Fatal(err)
	}
	
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS tasks (
		id TEXT PRIMARY KEY,
		status TEXT,
		result_url TEXT,
		detections TEXT,
		created_at DATETIME
	)`)
	
	return db
}