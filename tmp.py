import argparse
import os
import configparser

def read_configs(config_file:str)->dict:
    """
    Read configs from file & set values wthin them for Docker env params
    :args:
        config_file:str - config file to read
    :params:
        data:dict - content from config file
        parser:configparser.configparser.ConfigParser - configuration parser
    :return:
        if success return data, else return an error
    """
    data = {}
    if not os.path.isfile(config_file):
        return "Error: Unable to locate file '%s'" % config_file

    try:
        parser = configparser.ConfigParser()
    except Exception as e:
        return 'Error: Unable to create config parser object (Error: %s)' % e

    try:
        parser.read(config_file)
    except Exception as e:
        return "Error: Failed to read config file '%s' (Error: %s)" % (config_file, e)

    try:
        for section in parser.sections():
            for key in parser[section]:
                data[key.upper()] = parser[section][key].replace('"', '')
    except Exception as e:
        return "Failed to extract variables from config file '%s' (Error: %s)" % (config_file, e)

    return data


def format_content():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Send REST requests to configure an AnyLog instance.')
    parser.add_argument('config_file', type=str, default='$HOME/AnyLog-API/config/single-node.ini',
                        help='AnyLog INI config file')
    args = parser.parse_args()
    output = ""
    config_file = os.path.expandvars(os.path.expanduser(args.config_file))
    content = read_configs(config_file)

    for param in content:
        output += "\t-e %s=%s\n" % (param, content[param])

    print(output)
    
if __name__ == '__main__':
    format_content()
    