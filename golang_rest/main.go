package main
import (
//     "encode/json"
    "fmt"
    "net/http"
    "io/ioutil"
//     "reflect"
//     "strconv"
)

type ConnInfo struct {
    conn string // ip:port
    user string
    password string
}

var conn_info ConnInfo

//var conn string = "http://23.239.12.151:32349"

func statusConn(conn string, user string, password string) {
    conn_info.conn = "http://" + conn
    if user != "" || password != "" {
        conn_info.conn = "https://" + conn
    }
    conn_info.user = user
    conn_info.password = password
}

func get(command string, network bool, remote_conn string,  exception bool) (bool, string) {
    var status_code int64 = 200
    var status bool = true
    var content string = ""

    client := &http.Client{}
    req, _ := http.NewRequest("GET", conn_info.conn, nil)
    if conn_info.user != "" || conn_info.password != "" {
        req.SetBasicAuth(conn_info.user, conn_info.password)
    }

    req.Header.Add("command", command)
    req.Header.Add("user-agent", "AnyLog/1.23")
    if remote_conn != "" {
        req.Header.Add("destination", remote_conn)
    } else if network == true{
        req.Header.Add("destination", "network")
    }

    resp, err := client.Do(req)
    fmt.Sscan(resp.Status, &status_code)
    defer resp.Body.Close()
    if err != nil {
        status = false
        if exception == true {
            fmt.Println("Failed to execute GET for '", command, "' (Error: ", err, ")")
        }

    } else if status_code != 200 {
        status = false
        if exception == true {
            fmt.Println("Failed to execute GET for '",command,"' (Network Error: ", status_code, ")")
        }
    } else {
        body, _ := ioutil.ReadAll(resp.Body)
        content = string(body)
    }

    return status, content
}


func main() {
    statusConn("23.239.12.151:32349", "", "")

    status, content := get("get status", false, "", true)
    if status == true {
        fmt.Println(content)
    } else {
        fmt.Println("Failed get status")
    }

    fmt.Println("\n")
    status2, content2 := get("sql edgex format=json select * from rand_data limit 5", true, "", true)
    if status2 == true {
        fmt.Println(content2)
    } else {
        fmt.Println("Failed execute SQL")
    }
}