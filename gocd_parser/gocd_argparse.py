# Return an argparse object with all the standard GoCD arguments already
# filled in
import argparse

def get():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
            '-g', '--go_url',
            required=True,
            help='URL of the Go CD server, e.g. \
                    "http://gocd.example.com:8080/go"')
    arg_parser.add_argument(
            '-u', '--go_user',
            default='',
            help='User name of the account to access GoCD server',
            )
    arg_parser.add_argument(
            '-p', '--go_password',
            default='',
            help='Password of the account to access GoCD server',
            )
    return arg_parser
