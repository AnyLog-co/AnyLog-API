package main

import (
    "encoding/json"
    "fmt"
    "net/http"
    "io/ioutil"
    "time"

    "mypackage"
)

type ConnInfo struct {
    conn string // ip:port
    user string `default0:""`
    password string `default0:""`
    timeout time.Duration `default0:"30"`
}

var conn_info ConnInfo


func StatusConn(conn string, user string, password string, timeout int) {
    /**
    The following are the base support for AnyLog via REST
    - GET: extract information from AnyLog (information + queries)
    - POST: Execute or POST command against AnyLog
    - POST_POLICY: POST information to blockchain
    :url:
    https://github.com/AnyLog-co/documentation/blob/master/using%20rest.md
    :global:
        conn_info ConnInfo - Golang structure that stores (static) connection information
    :args:
        conn string - IP:port connection information
        user string - if authenticated the user to request with
        password string - password associated with the user
        timeout int - REST timeout value
    */
    conn_info.conn = "http://" + conn
    if user != "" || password != "" {
        conn_info.conn = "https://" + conn
    }
    conn_info.user = user
    conn_info.password = password
    conn_info.timeout = time.Duration(timeout)
}

func GetConnInfo() ConnInfo {
    return conn_info
}
//
func Get(command string, network bool, remote_conn string,  exception bool) (bool, string){
    /**
    requests GET command
    :args:
        command string - REST request to execute
        network bool - whether to request a remote node (true) or local node (false)
        remote_conn string - if against a remote node, the you can sepcify the IP:port of said node(s) otherwise will scan the entire network
        exception:bool - whether to print exceptions
    :param:
        status bool
        status_code int - REST status code
        content string - content returned from REST request
    :return:
        status, content
    */
    var status_code int = 200
    var status bool = true
    var content string = ""

    // prepare GET request connection
    client := &http.Client{
        Timeout: conn_info.timeout * time.Second,
    }
    req, _ := http.NewRequest("GET", conn_info.conn, nil)
    if conn_info.user != "" || conn_info.password != "" {
        req.SetBasicAuth(conn_info.user, conn_info.password)
    }

    //prepare headers
    req.Header.Add("command", command)
    req.Header.Add("user-agent", "AnyLog/1.23")
    if remote_conn != "" {
        req.Header.Add("destination", remote_conn)
    } else if network == true{
        req.Header.Add("destination", "network")
    }

    // execute GET request
    resp, err := client.Do(req)
    fmt.Sscan(resp.Status, &status_code)
    defer resp.Body.Close()

    // if error in request - generate error message
    if err != nil {
        status = false
        output := mypackage.PrintRESTError("GET", command, status_code, err)
        if exception == true{
            fmt.Println(output)
        }
    } else {
        // extract results from GET request
        body, err := ioutil.ReadAll(resp.Body)
        if err != nil { // if error in generating results - generate error message
            status = false
            output := mypackage.PrintRESTError("OUTPUT", command, 200, err)
            if exception == true {
                fmt.Println(output)
            }
        } else { // extract content
            content = string(body)
        }
    }

    return status, content
}

func main() {
    var status bool
    var content string

    StatusConn("23.239.12.151:32349", "", "", 30)
    status, content = Get("get status", false, "", true)
    if status == true {
        fmt.Println(content)
    }

    status, content = Get("sql edgex format=table select count(*) from rand_data", true, "", true)
    if status == true {
        fmt.Println(content)
    }

    status, content = Get("sql edgex stat=false and format=json select count(*) from rand_data", true, "", true)
    if status == true { // convert JSON output to mapping format
        var data map[string]interface{}
        json.Unmarshal([]byte(content), &data)
        fmt.Println("\n", data, "\n")
    }
}
