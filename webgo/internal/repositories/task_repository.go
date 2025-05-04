package repositories

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	"backend/internal/models"
)

type TaskRepository struct {
	db *sql.DB
}

func NewTaskRepository(db *sql.DB) *TaskRepository {
	return &TaskRepository{db: db}
}

func (r *TaskRepository) Create(task *models.Task) error {
	detections, _ := json.Marshal(task.Detections)
	_, err := r.db.Exec(
		"INSERT INTO tasks VALUES (?, ?, ?, ?, ?)",
		task.ID, task.Status, task.ResultURL, detections, task.CreatedAt,
	)
	return err
}


func (r *TaskRepository) GetAll() ([]*models.Task, error) {
    rows, err := r.db.Query("SELECT id, status, result_url, detections, created_at FROM tasks ORDER BY created_at DESC")
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var tasks []*models.Task
    for rows.Next() {
        var task models.Task
        var detectionsJson string
        var createdAt string

        err := rows.Scan(
            &task.ID,
            &task.Status,
            &task.ResultURL,
            &detectionsJson,
            &createdAt,
        )
        if err != nil {
            return nil, err
        }

        // Парсинг времени
        task.CreatedAt, _ = time.Parse(time.RFC3339, createdAt)
        
        // Парсинг детекций
        if detectionsJson != "" {
            if err := json.Unmarshal([]byte(detectionsJson), &task.Detections); err != nil {
                return nil, err
            }
        }

        tasks = append(tasks, &task)
    }

    return tasks, nil
}

func (r *TaskRepository) GetByID(id string) (*models.Task, error) {
    var task models.Task
    var detectionsJson string
    var createdAt string

    err := r.db.QueryRow(
        "SELECT id, status, result_url, detections, created_at FROM tasks WHERE id = ?",
        id,
    ).Scan(
        &task.ID,
        &task.Status,
        &task.ResultURL,
        &detectionsJson,
        &createdAt,
    )

    if err != nil {
        if err == sql.ErrNoRows {
            return nil, fmt.Errorf("task not found")
        }
        return nil, err
    }

    // Парсинг времени
    task.CreatedAt, _ = time.Parse(time.RFC3339, createdAt)
    
    // Парсинг детекций
    if detectionsJson != "" {
        if err := json.Unmarshal([]byte(detectionsJson), &task.Detections); err != nil {
            return nil, err
        }
    }

    return &task, nil
}



// Добавить в TaskRepository
func (r *TaskRepository) GetAllByStatus(status string) ([]*models.Task, error) {
    rows, err := r.db.Query(
        "SELECT id, status, result_url, detections, created_at FROM tasks WHERE status = ?",
        status,
    )
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var tasks []*models.Task
    for rows.Next() {
        var task models.Task
        var detectionsJson string
        var createdAt string

        err := rows.Scan(
            &task.ID,
            &task.Status,
            &task.ResultURL,
            &detectionsJson,
            &createdAt,
        )
        if err != nil {
            return nil, err
        }

        task.CreatedAt, _ = time.Parse(time.RFC3339, createdAt)
        if detectionsJson != "" {
            json.Unmarshal([]byte(detectionsJson), &task.Detections)
        }

        tasks = append(tasks, &task)
    }

    return tasks, nil
}

func (r *TaskRepository) Update(task *models.Task) error {
    detectionsJson, _ := json.Marshal(task.Detections)
    _, err := r.db.Exec(
        "UPDATE tasks SET status = ?, result_url = ?, detections = ? WHERE id = ?",
        task.Status,
        task.ResultURL,
        string(detectionsJson),
        task.ID,
    )
    return err
}