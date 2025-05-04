package models

import "fmt"

func (t *Task) FilePath() string {
    return fmt.Sprintf("uploads/%s", t.ID)
}