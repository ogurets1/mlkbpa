package config

type Config struct {
	Port         string
	DBPath     string 
	MLServiceURL string
	UploadPath   string
}

func LoadConfig() *Config {
	return &Config{
		Port:         "8080",
		DBPath: "tasks.",
		UploadPath:   "./uploads",
		MLServiceURL: "http://ml-service:8000/process",
	}
}