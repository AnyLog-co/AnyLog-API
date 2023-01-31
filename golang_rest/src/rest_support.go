/**
For package to be called upon, it needs to seat in /usr/local/Cellar/go/1.17.1/libexec/src/mypackage/
*/
package mypackage
import (
    "fmt"
    "strconv"
)

func PrintRESTError(call_type string, cmd string, status_code int, err error) string{
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

