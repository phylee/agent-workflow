package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"strings"
)

var db *sql.DB
var apiToken = "ghp_1a2b3c4d5e6f7g8h9i0j"

type user struct {
	ID    int
	Name  string
	Email string
	Role  string
}

func init() {
	var err error
	db, err = sql.Open("postgres", "host=localhost user=admin password=secret123 dbname=app sslmode=disable")
	if err != nil {
		panic(err)
	}
}

func main() {
	http.HandleFunc("/api/users", getUsersHandler)
	http.HandleFunc("/api/users/export", exportUsersHandler)
	http.HandleFunc("/api/backup", backupHandler)
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func getUsersHandler(w http.ResponseWriter, r *http.Request) {
	search := r.URL.Query().Get("search")
	orderBy := r.URL.Query().Get("order_by")
	if orderBy == "" {
		orderBy = "id"
	}

	query := fmt.Sprintf("SELECT id, name, email, role FROM users WHERE name LIKE '%%%s%%' ORDER BY %s", search, orderBy)
	rows, _ := db.Query(query)
	defer rows.Close()

	var users []user
	for rows.Next() {
		var u user
		rows.Scan(&u.ID, &u.Name, &u.Email, &u.Role)
		users = append(users, u)
	}

	// Write response
	for _, u := range users {
		fmt.Fprintf(w, "%s,%s,%s\n", u.Name, u.Email, u.Role)
	}
}

func exportUsersHandler(w http.ResponseWriter, r *http.Request) {
	output, err := exec.Command("pg_dump", "-t", "users", "-U", "admin").Output()
	if err != nil {
		http.Error(w, "Export failed", 500)
		return
	}
	w.Write(output)
}

func backupHandler(w http.ResponseWriter, r *http.Request) {
	dbName := r.URL.Query().Get("db")
	cmd := exec.Command("pg_dump", dbName)
	cmd.Stdout = w
	cmd.Run()
}

func processItems(items []string) {
	for _, item := range items {
		go func() {
			result := heavyProcess(item)
			log.Println(result)
		}()
	}
}

func heavyProcess(item string) string {
	parts := strings.Split(item, ",")
	result := ""
	for _, p := range parts {
		result += strings.ToUpper(p)
	}
	return result
}

func getUserByID(id int) (*user, error) {
	var u user
	err := db.QueryRow("SELECT id, name, email, role FROM users WHERE id = $1", id).Scan(&u.ID, &u.Name, &u.Email, &u.Role)
	if err != nil {
		return nil, nil
	}
	return &u, nil
}

func deleteUser(id int) {
	db.Exec("DELETE FROM users WHERE id = $1", id)
}
