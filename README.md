
# Swhunt

A tool is checking the auth on swagger json
# Installation

```
git cloen https://github.com/alanEG/swhunt
cd swhunt
python3 swhunt.py 
```
## Documentation
Swhunt has many argument 
You can run `./swhunt.py -h` to show help 
```
                 __                __
 .-----.--.--.--|  |--.--.--.-----|  |_
 |__ --|  |  |  |     |  |  |     |   _|
 |_____|________|__|__|_____|__|__|____|
              # version 1.0 (beta)
              # @author alanEG
usage: swhunt.py [-h] -t TARGET [-H HEADER] [-x PROXY] [-r REPL] [-o OUTPUT] [-s SERVER] [-as ALL_SERVER] [-nc NO_COLOR]
optional arguments:
  -h, --help            show this help message and exit
  -t TARGET, --target TARGET
                        Swagger target [file,url]
  -H HEADER, --header HEADER
                        Custom header Ex, -H 'Test: Test'
  -x PROXY, --proxy PROXY
                        Custom proxy
  -r REPL, --replace REPL
                        Replace value in header or body Ex, -r 'name: value'
  -o OUTPUT, --output OUTPUT
                        Output file
  -s SERVER, --server SERVER
                        Api url
  -as ALL_SERVER, --all-servers ALL_SERVER
                        Check each path on each server in swagger object
  -nc NO_COLOR, --no-color NO_COLOR
                        No color
```
- `-t|-target url|file`

    This argument take the input the input should be url or file 
- `-H|-header 'header_name: header_alue'`
    
    It takes the header for requests 

    If the header is aleardy exist the value will replaced by the value you did pass in the argument

    If you need to pass many header all you need to do is `-H 'h_n1: h_v1' -H 'h_n2: h_v2'`

- `-r|--replace 'name: value'`
    
    This is option take name and value from input and replace any parameter with the same name to value provided

- `-s|--server api_server`
    
    This option takes the server the tool will send the requests to

- `-as|--all-servers`

    If there many server in swagger server this option allow to us to test the endpoints on all servers 
    Including the server did you include in `--server`  
