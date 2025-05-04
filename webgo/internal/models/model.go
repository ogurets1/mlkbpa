package models

import "time"

type Detection struct {
	Class      string  `json:"class"`
	Confidence float64 `json:"confidence"`
	BBox       []int   `json:"bbox"`
}

type Task struct {
	ID         string      `json:"id"`
	Status     string      `json:"status"`
	ResultURL  string      `json:"result_url"`
	Detections []Detection `json:"detections"`
	CreatedAt  time.Time   `json:"created_at"`
}
