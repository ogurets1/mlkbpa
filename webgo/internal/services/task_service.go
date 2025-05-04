package services

import (
	"database/sql"
	"log"

	"time"

	"backend/internal/config"
	"backend/internal/models"
	"backend/internal/pkg/mlclient"
	"backend/internal/repositories"
)

type TaskService struct {
	repo   *repositories.TaskRepository
	cfg    *config.Config
	mlServ *mlclient.MLClient
}

func NewTaskService(db *sql.DB, cfg *config.Config) *TaskService {
	return &TaskService{
		repo:   repositories.NewTaskRepository(db),
		cfg:    cfg,
		mlServ: mlclient.NewMLClient(cfg.MLServiceURL),
	}
}

func (s *TaskService) ProcessQueue() {
	ticker := time.NewTicker(5 * time.Second)
	for range ticker.C {
		s.processPendingTasks()
	}
}

func (s *TaskService) CreateTask(task *models.Task) error {
	return s.repo.Create(task)
}

func (s *TaskService) GetAllTasks() ([]*models.Task, error) {
	return s.repo.GetAll()
}

func (s *TaskService) GetTaskByID(id string) (*models.Task, error) {
	return s.repo.GetByID(id)
}


func (s *TaskService) processPendingTasks() {
    tasks, err := s.repo.GetAllByStatus("processing")
    if err != nil {
        log.Printf("Error fetching pending tasks: %v", err)
        return
    }

    for _, task := range tasks {
        // Обработка изображения через ML-сервис
        detections, resultURL, err := s.mlServ.ProcessImage(task.FilePath())
        if err != nil {
            log.Printf("Failed to process task %s: %v", task.ID, err)
            continue
        }

        // Обновление статуса задачи
        task.Status = "completed"
        task.Detections = detections
        task.ResultURL = resultURL

        if err := s.repo.Update(task); err != nil {
            log.Printf("Failed to update task %s: %v", task.ID, err)
        }
    }
}
