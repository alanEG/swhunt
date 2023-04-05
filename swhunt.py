#/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

import json, sys, argparse, urllib3
from core.printm import *
from core.swagger_handler import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
def run(target):
    color(args.no_color)
    _swagger_handler = swagger_handler(args)

    if target.startswith('http://') or target.startswith('https://'):
        response = requests.get(target,proxies=args.proxy,verify=False)
        if response.status_code != 200:
            pm(msn=2,target=target)
            return None
        try:
            _swagger_handler.get_content(json.loads(response.text))
        except json.decoder.JSONDecodeError:
            pm(msn=1,target=target)
            sys.exit(1)
    else: 
        try:
            with open(target) as F:
                _swagger_handler.get_content(json.loads(F.read()))
        except FileNotFoundError:
            pm(msn=3,target=target)
            sys.exit()
        except json.decoder.JSONDecodeError:
            pm(msn=2,target=target)
            sys.exit()
    
    swcontents = _swagger_handler.swcontents
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for path in swcontents['paths']:
            future = executor.submit(
                _swagger_handler.preper_request,
                swcontents['paths'][path],
                path,
                swcontents['server'],
                args)
            futures.append(future)
        
        # Wait for all futures to complete and check for exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Exception occurred: {e}")
    
    if args.output:
        _swagger_handler.save_output(args.output)

def main():
    pm(msn=5)
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("-t","--target",help="Swagger target [file,url]",required=True)
    parser.add_argument("-H", "--header",help="Custom header Ex, -H 'Test: Test'", action='append')
    parser.add_argument("-x","--proxy",help="Custom proxy")
    parser.add_argument("-r","--replace",help="Replace value in header or body Ex, -r 'name: value'", action='append',dest='repl')
    parser.add_argument("-o","--output",help="Output file")
    parser.add_argument("-s","--server",help="Api url",default="")
    parser.add_argument("-as","--all-servers",help="Check each path on each server in swagger object",dest="all_servers")
    parser.add_argument("-nc","--no-color",help="No color",dest="no_color",action="store_true")
    args = parser.parse_args()
    
    if args.proxy:
        proxy_args_split = args.proxy.split(':')
        args.proxy = {proxy_args_split[0]:args.proxy,}

    if len(sys.argv) > 1:
        run(args.target)

    else:
        parser.print_usage()

if __name__ == '__main__':
    main()