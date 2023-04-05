
# swhunt
swhunt is a command-line tool that helps you test RESTful APIs defined using Swagger/OpenAPI 3.x specification. The tool reads the Swagger file, generates requests based on the provided endpoint information, and sends them to the server. It then collects the response and provides detailed information on the result

## Usage
You can run `./swhunt.py -h` to show help 
```
                 __                __
 .-----.--.--.--|  |--.--.--.-----|  |_
 |__ --|  |  |  |     |  |  |     |   _|
 |_____|________|__|__|_____|__|__|____|
              # version 1.0
              # @author alanEG
usage: swhunt.py [-h] -t TARGET [-H HEADER] [-x PROXY] [-r REPL] [-o OUTPUT] [-s SERVER] [-as ALL_SERVERS] [-nc]

optional arguments:
  -h, --help            show this help message and exit
  
  -t, --target          Swagger target [file,url]
  
  -H, --header          Custom header Ex, -H 'Test: Test'
  
  -x, --proxy           Custom proxy
  
  -r, --replace         Replace value in header or body Ex, -r 'name: value'
  
  -o, --output          Output file
  
  -s, --server          Api url
  
  -as, --all-servers    Check each path on each server in swagger object
  
  -nc, --no-color       No color
```

-t|--target url|file:

    This argument is used to specify the target input, which can be either a URL or a file. If the Swagger version is less than 3.x, you should use the following command to convert it to version 3.x or convert from YAML to JSON:

    `python3 swhunt.py -t https://converter.swagger.io/api/convert?url={url}`

-H|--header 'header_name: header_value':

    This argument takes the header for requests.

    If the header already exists, the value will be replaced by the value you pass in the argument.

    If you need to pass many headers, all you need to do is `-H 'h_n1: h_v1' -H 'h_n2: h_v2'`.

-x|--proxy 'http(s)://proxy-url:port':

    This argument sets the proxy for requests.

-r|--replace 'name: value':

    This argument replaces the value in headers or body.

-o|--output output_file:

    This argument specifies the output file name.

-s|--server server_url:

    The -s|--server argument specifies the URL of the server to which requests should be sent. Use this option when there is no server URL specified in the Swagger file.

-as|--all-servers:

    This argument checks each path on each server in the swagger object 
    Include the server passing in the argument and the servers in swagger.json.

-nc|--no-color:

    This argument disables the color output.

# Contributing
We welcome contributions to swhunt! If you'd like to contribute, please fork the repository and submit a pull request. You can also create an issue to report a bug or request a new feature.