package main

import (
	
	"backend/internal/config"
	"backend/pkg/database"
	"backend/internal/routes"
	"backend/internal/services"
)

func main() {
	cfg := config.LoadConfig()
	
	db := database.InitDB(cfg)
	defer db.Close()
	
	taskService := services.NewTaskService(db, cfg)
	go taskService.ProcessQueue()
	
	r := routes.SetupRouter(taskService)
	r.Run(":" + cfg.Port)
}