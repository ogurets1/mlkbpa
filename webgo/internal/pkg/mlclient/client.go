package mlclient

import (
	"backend/internal/models"
	"bytes"
	"encoding/json"
	"io"
	"mime/multipart"
	"net/http"
	"os"
)

type MLClient struct {
	baseURL string
}

func NewMLClient(baseURL string) *MLClient {
	return &MLClient{baseURL: baseURL}
}

func (c *MLClient) ProcessImage(filePath string) ([]models.Detection, string, error) {
	// Реализация вызова ML-сервиса
	// Полная реализация будет выглядеть примерно так:
	file, err := os.Open(filePath)
	if err != nil {
		return nil, "", err
	}
	defer file.Close()

	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)
	part, _ := writer.CreateFormFile("image", file.Name())
	io.Copy(part, file)
	writer.Close()

	resp, err := http.Post(c.baseURL, writer.FormDataContentType(), body)
	if err != nil {
		return nil, "", err
	}
	defer resp.Body.Close()

	var result struct {
		Detections []models.Detection `json:"detections"`
		ResultURL  string             `json:"result_url"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, "", err
	}

	return result.Detections, result.ResultURL, nil
}