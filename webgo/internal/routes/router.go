package routes

import (
	"backend/internal/controllers"
	"backend/internal/services"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func SetupRouter(taskService *services.TaskService) *gin.Engine {
	router := gin.Default()
	
	// Настройка CORS
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"},
		AllowMethods:     []string{"GET", "POST"},
		AllowHeaders:     []string{"Origin", "Content-Type"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge: 12 * time.Hour,
	}))
	
	tc := controllers.NewTaskController(taskService)
	
	api := router.Group("/api")
	{
		api.POST("/upload", tc.Upload)
		api.GET("/tasks", tc.GetTasks)
		api.GET("/tasks/:id", tc.GetTask)
	}
	
	return router
}