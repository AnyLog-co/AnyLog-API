package main
import (
    "fmt"
    "mypackage"
)

func main() {
    mypackage.StatusConn("127.0.0.1:32349", "", "", 30)
    conn_info := mypackage.GetConnInfo()
    fmt.Println(conn_info)
    status, content := mypackage.Get("get status", false, "", true)
    fmt.Println(status)
    fmt.Println(content)
}