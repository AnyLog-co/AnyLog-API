// Generic GET:  https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#get-command

package main
import (
    "mypackage"
//    "encoding/json"
    "fmt"
//    "strconv"
    "strings"

)



func GetStatus(json_format bool, view_help bool, exception bool) bool {
    /**
    check if node is running
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-status-command
    :args:
        json_format bool - whether to get the results in JSON format
        view_help bool - whether to get help information for node
        exception bool - whether to print exceptions
    :params:
        status bool
        command string - command to execute
        content string - output from GET request
    :return:
        true if success
        fals if fails
        nil if view help
    */
    var status bool
    var command string = "get status"
    if json_format == true {
        command += " where format=json"
    }

    if view_help == true {
        HelpCommand(command, exception)
        status = true
    } else {
        status, content := mypackage.Get(command, false, "", exception)
        if status == true && (! strings.Contains(content, "running") || strings.Contains(content, "not")) {
                status = false
        }
    }

    return status
}


func HelpCommand(user_command string, exception bool) {
    /**
    Given a command, get the `help` output for it
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/getting%20started.md#the-help-command
    :args:
        user_commmand string - command to get help for
        exception bool - whether to print exceptions
    :params:
        status bool
        command string - (help) command to execute
        content string - results from help request
    */

    var command string = "help"
    if command != "" {
        command += " " + user_command
    }

    status, content := mypackage.Get(command, false, "", exception)
    if status == true {
        fmt.Println(content)
    }
}

func main() {
    mypackage.StatusConn("23.239.12.151:32349", "", "", 30)
    status := GetStatus(true,  true, true)


}