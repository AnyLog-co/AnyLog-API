package mypackage

import (
//    "encoding/json"
    "fmt"
    "net/http"
    "io/ioutil"
    "strconv"
    "time"
)

type ConnInfo struct {
    conn string // ip:port
    user string `default0:""`
    password string `default0:""`
    timeout time.Duration `default0:"30"`
}

var conn_info ConnInfo

func printRESTError(call_type string, cmd string, status_code int, err error) string{
    /**
    generate Error message based on user information
    :args:
        call_type string - REST request executed
        cmd       string - command that was executed by user
        status_code int  - REST status code
        error     string - REST error message
    :params:
        error_msg string - generated error message
        network_errors_generic  map - dictionary of possible (generic) REST error messages
        network_errors          map - dictionary of possible (detailed) REST error messages
    :return:
        error_msg
    */
    var error_msg string = "Failed to execute " + call_type + " for " + cmd

    network_errors_generic := map[int]string{
        1: "Informational",
        2: "Successful",
        3: "Redirection",
        4: "Client Error",
        5: "Server Error",
        7: "Developer Error",
    }

    network_errors := map[int]string{
        100: "Continue",
        101: "Switching Protocols",
        200: "OK",
        201: "Created",
        202: "Accepted",
        203: "Non-Authoritative Information",
        204: "No Content",
        205: "Reset Content",
        206: "Partial Content",
        300: "Multiple Choices",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        305: "Use Proxy",
        307: "Temporary Redirect",
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request Timeout",
        409: "Conflict",
        410: "Gone",
        411: "Length Required",
        412: "Precondition Failed",
        413: "Payload Too Large",
        414: "URI Too Long",
        415: "Unsupported Media Type",
        416: "Range Not Satisfiable",
        417: "Expectation Failed",
        418: "I'm a teapot",
        426: "Upgrade Required",
        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Time-out",
        505: "HTTP Version Not Supported",
        102: "Processing",
        207: "Multi-Status",
        226: "IM Used",
        308: "Permanent Redirect",
        422: "Unprocessable Entity",
        423: "Locked",
        424: "Failed Dependency",
        428: "Precondition Required",
        429: "Too Many Requests",
        431: "Request Header Fields Too Large",
        451: "Unavailable For Legal Reasons",
        506: "Variant Also Negotiates",
        507: "Insufficient Storage",
        511: "Network Authentication Required",
    }

    if status_code != 200 {
        if _, ok := network_errors[status_code]; ok {
            error_msg += " (Network Error " + strconv.Itoa(status_code) + " - " + network_errors[status_code] + ")"
        } else if status_code < 200 {
            error_msg += " (Network Error " + strconv.Itoa(status_code) + " - " + network_errors_generic[1] + ")"
        } else if status_code < 300 {
            error_msg += " (Network Error " + strconv.Itoa(status_code) + " - " + network_errors_generic[2] + ")"
        } else if status_code < 400 {
            error_msg += " (Network Error " + strconv.Itoa(status_code) + " - " + network_errors_generic[3] + ")"
        } else if status_code < 500 {
            error_msg += "(Network Error " + strconv.Itoa(status_code) + " - " + network_errors_generic[4] + ")"
        } else if status_code < 600 {
            error_msg += "(Network Error " + strconv.Itoa(status_code) + " - " + network_errors_generic[5] + ")"
        } else if status_code < 800 {
            error_msg += " (Network Error " + strconv.Itoa(status_code) + " - " + network_errors_generic[7] + ")"
        }
    } else if err != nil {
        error_msg += " (Error: " + fmt.Sprint(err) + ")"
    } else { // if no error then reset to empty value
        error_msg = ""
    }

    return error_msg
}

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
        output := printRESTError("GET", command, status_code, err)
        if exception == true{
            fmt.Println(output)
        }
    } else {
        // extract results from GET request
        body, err := ioutil.ReadAll(resp.Body)
        if err != nil { // if error in generating results - generate error message
            status = false
            output := printRESTError("OUTPUT", command, 200, err)
            if exception == true {
                fmt.Println(output)
            }
        } else { // extract content
            content = string(body)
        }
    }
    req.Header.Add("command", command)
    req.Header.Add("user-agent", "AnyLog/1.23")
    if remote_conn != "" {
        req.Header.Add("destination", remote_conn)
    }


    return status, content
}

//func Post(command string, topic string, remote_conn string,  payload string, exception bool) bool {
//    /**
//    Execute POST command against AnyLog. payload is required under the following conditions:
//        1. payload can be data that you want to add into AnyLog, in which case you should also have an
//        MQTT client of type REST running on said node
//        2. payload can be a policy you'd like to add into the blockchain
//        3. payload can be a policy you'd like to remove from the blockchain
//        note only works with Master, cannot remove a policy on a real blockchain like Ethereum.
//    :args:
//        command string - command to execute
//        topic string - topic correlated to the MQTT client using a REST
//        remote_conn string - if you'd like to forward the POST request (usually master node for declaring policies)
//        payload string - JSON string to be stored
//        exception:bool - whether to print exceptions
//    :param:
//        status bool
//        status_code int - REST status code
//    :return:
//        status
//    */
//    var status_code int = 200
//    var status bool = true
//
//    // prepare POST connection
//    client := &http.Client{
//        Timeout: conn_info.timeout * time.Second,
//    }
//    if payload != "" {
//        req, _ := http.NewRequest("POST", conn_info.conn, bytes.NewBuffer(payload))
//    } else {
//        req, _ := http.NewRequest("POST", conn_info.conn, nil)
//    }
//    if conn_info.user != "" || conn_info.password != "" {
//        req.SetBasicAuth(conn_info.user, conn_info.password)
//    }
//
//    // prepare Headers
//    req.Header.Add("command", command)
//    req.Header.Add("user-agent", "AnyLog/1.23")
//    if remote_conn != "" {
//        req.Header.Add("destination", remote_conn)
//    }
//    if topic != "" {
//        req.Header.Add("topic", topic)
//    }
//
//    // Execute POST command
//    resp, err := client.Do(req)
//    fmt.Sscan(resp.Status, &status_code)
//    defer resp.Body.Close()
//
//    // if error in request - generate error message
//    if err != nil {
//        status = false
//        output := printRESTError("POST", command, status_code, err)
//        if exception == true{
//            fmt.Println(output)
//        }
//    }
//
//    return status
//
//}
//
//func Put(dbms string, table string, mode string, payload string, exception bool) bool {
//    /**
//    Execute a PUT command against AnyLog - mainly used for Data
//    :args:
//        dbms string - logical database to store in
//        table string - table to store data in
//        mode string - whether to PUT data continuously (streaming) or one at a time (file)
//        payload string - JSON string to be stored
//        exception:bool - whether to print exceptions
//    :param:
//        status bool
//        status_code int - REST status code
//    :return:
//        status
//    */
//    var status_code int = 200
//    var status bool = true
//
//    // prepare POST connection
//    client := &http.Client{
//        Timeout: conn_info.timeout * time.Second,
//    }
//
//    req, _ := http.NewRequest("PUT", conn_info.conn, bytes.NewBuffer(payload))
//
//    // prepare Headers
//    req.Header.Add("type", "json")
//    req.Header.Add("dbms", dbms)
//    req.Header.Add("table", table)
//    if mode == "streaming" || mode == "file" {
//        req.Header.Add("mode", mode)
//    } else {
//        req.Header.Add("mode", "streaming")
//    }
//    req.Header.Add("Content-Type", "text/plain")
//
//
//    // Execute POST command
//    resp, err := client.Do(req)
//    fmt.Sscan(resp.Status, &status_code)
//    defer resp.Body.Close()
//
//    // if error in request - generate error message
//    if err != nil {
//        status = false
//        output := printRESTError("PUT", command, status_code, err)
//        if exception == true{
//            fmt.Println(output)
//        }
//    }
//
//    return status
//
//}
