package controllers

import (
	"backend/internal/models"
	"backend/internal/services"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

type TaskController struct {
	service *services.TaskService
}

func NewTaskController(s *services.TaskService) *TaskController {
	return &TaskController{service: s}
}


// Upload обрабатывает загрузку файла
func (c *TaskController) Upload(ctx *gin.Context) {
	// Получаем файл из запроса
	file, err := ctx.FormFile("file")
	if err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "File upload failed"})
		return
	}

	// Генерируем уникальный ID задачи
	taskID := uuid.New().String()
	
	// Сохраняем файл
	filePath := "uploads/" + taskID + "-" + file.Filename
	if err := ctx.SaveUploadedFile(file, filePath); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}

	// Создаем задачу в базе данных
	task := &models.Task{
		ID:        taskID,
		Status:    "processing",
		CreatedAt: time.Now(),
	}
	
	if err := c.service.CreateTask(task); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create task"})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{
		"id":     taskID,
		"status": task.Status,
	})
}

// GetTasks возвращает список всех задач
func (c *TaskController) GetTasks(ctx *gin.Context) {
	tasks, err := c.service.GetAllTasks()
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch tasks"})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"tasks": tasks})
}

// GetTask возвращает задачу по ID
func (c *TaskController) GetTask(ctx *gin.Context) {
	taskID := ctx.Param("id")
	if taskID == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Task ID is required"})
		return
	}

	task, err := c.service.GetTaskByID(taskID)
	if err != nil {
		ctx.JSON(http.StatusNotFound, gin.H{"error": "Task not found"})
		return
	}

	ctx.JSON(http.StatusOK, task)
}