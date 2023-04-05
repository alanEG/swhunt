import requests, sys, re, traceback, json
from core.printm import pm
from urllib import parse

class swagger_handler:
    def __init__(self,args):
        self.args = args
        self.components = ""
        self.swcontents = ""

    def get_swcontents(self):
        return self.swcontents

    def get_ref(self,ref):
        obnt=self.components
        for obj in ref[2:].split('/')[1:]:
            obnt = obnt[obj]
        return obnt 

    def switch_type(self,obj_i,obj_name='',ref_name='',ref_count=0):
        """
            Switches the type of a given object and returns a value based on the type.
        """
        if "$ref" in obj_i.keys():
            # If the object contains a reference, get the referenced object
            ref = self.get_ref(obj_i["$ref"])

            if ref_name == obj_i["$ref"]:
                # Avoid infinite loop caused by self-referencing
                if ref_count > 1:
                    return "test"
                ref_count+=1
            return self.get_object(ref,obj_name=obj_name,ref_name=obj_i['$ref'],ref_count=ref_count)

        elif "array" in obj_i['type']:
            # If the object is an array, recursively call this function on the items in the array.
            return [self.switch_type(obj_i['items'],obj_name=obj_name,ref_name=ref_name,ref_count=ref_count)]

        elif "object" in obj_i['type']:
            # If the object is an object, recursively call this function on any additional properties
            if "additionalProperties" in obj_i.keys() and obj_i['additionalProperties'] != {} and obj_i['additionalProperties'] != False:
                return self.get_object(obj_i['additionalProperties'],obj_name=obj_name,ref_name=ref_name,ref_count=ref_count)
            else:
                if "nullable" in obj_i.keys():
                    return {}
                return self.get_object(obj_i,obj_name=obj_name)

        elif "string" in obj_i['type']:
            # If the object is a string, return a string value.
            if "format" in obj_i.keys() and "binary" in obj_i['format']:
                return self.set_parameter_value(obj_i,"binary",obj_name)
            return self.set_parameter_value(obj_i,"string",obj_name)

        elif "boolean" in obj_i['type']:
            # If the object is a boolean, return a boolean value
            return self.set_parameter_value(obj_i,True,obj_name)
        
        elif "integer" in obj_i['type']:
            # If the object is an integer, return an integer value.
            return self.set_parameter_value(obj_i,1,obj_name)
        
        elif "number" in obj_i['type']:
            # If the object is a number, return a number value.
            return self.set_parameter_value(obj_i,1,obj_name)
        else:
            # If the object type is not supported, return an empty dictionary.
            print(f"type {obj_i['type']} not supported")
            out = {}
            return out
        
    def set_parameter_value(self,inp,else_value,parameter_name):
        """
            Given a schema for a parameter, determine its default value or return a value from the args.
        """
        if self.args.repl:
            for arg in self.args.repl: 
                arg_split = arg.split(":")
                if arg_split[0] == parameter_name:
                    return arg_split[1].replace(' ','')
            return self.set_defualt_value(inp,else_value)       
        else:
            return self.set_defualt_value(inp,else_value)

    def set_defualt_value(self,inp,else_value):
        """
            Returns the default value of a parameter.

            If the parameter has an 'enum' field, the first value in the 'enum' field is returned.
            Otherwise, if the parameter has a 'default' field, its value is returned.
            If neither of the above cases are true, the else_value parameter is returned
        """
        if "enum" in inp.keys():
            return inp['enum'][0]
        elif "default" in inp.keys():
            return inp['default']
        return else_value

    def get_object(self,schema,obj_name='',ref_name='',ref_count=0):
        """
            Takes in a JSON schema object and returns a Python dictionary representing the object.
        """
        out = {}
        # Check if the current schema object has properties, if so, process them
        if "properties" in schema.keys():
            for prop_name, prop_schema in schema['properties'].items():
                switch_out = self.switch_type(prop_schema, obj_name=prop_name, ref_name=ref_name, ref_count=ref_count)
                # If switch_out is a single key dictionary, unpack it
                if isinstance(switch_out, dict) and len(switch_out.keys()) == 1 and list(switch_out.keys())[0] == prop_name:
                    out.update(switch_out)
                else:
                    out.update({prop_name: switch_out})
        else:
            # Process the schema object with switch_type function
            switch_out = self.switch_type(schema, obj_name=obj_name, ref_name=ref_name, ref_count=ref_count)
            if isinstance(switch_out, dict):
                out.update(switch_out)
            else:
                return switch_out
        return out

    def get_content_type(self,item_types):
        """
            Get the content type from the list of item types.
        """
        for item_type in item_types:
            if "application/json" == item_type.split(';')[0] or "multipart/form-data" == item_type.split(';')[0]:
                return item_type
        pm(msn=6,contentTypes=item_types)
        sys.exit()

    def get_request_body(self,request_body):
        """
            Returns the request body object and content type.
        """
        content_type = self.get_content_type(list(request_body['content'].keys()))
        schema = request_body['content'][content_type]['schema']
        if "$ref" in schema.keys():
            ref = self.get_ref(schema['$ref'])
            return self.get_object(ref), content_type

        elif "type" in schema.keys():
            return self.get_object(schema), content_type
        

    # for loop for each path then get the parameters 
    # if the path is method has content in it's body 
    # we use the function getRequestBody for get the request body   
    def get_swagger_path(self,swagger_content):
        """
            Extracts and prepares the paths and methods with their parameters and request body 
            from a Swagger/OpenAPI JSON content.
        """

        prepared_object = {}

        # Loop through each path and get the parameters
        for path in swagger_content['paths'].keys():
            path_object = swagger_content['paths'][path]
            methods = path_object.keys()

            # Add the methods as JSON object in the path object 
            prepared_object.update({path:{method:{"parameter":{}} for method in methods}})

            # Get the parameters information related to the method 
            for method in methods:
                path_object_method = path_object[method]
                
                # Check if the path has parameter
                if 'parameters' in path_object_method.keys():
                    parameters = path_object_method['parameters']
                    for parameter in parameters:
                        # Check if the parameter is reference to ref in the components
                        if "$ref" in parameter['schema']: 
                            param_value = self.get_ref(parameter['schema']["$ref"])['type']
                        else:
                            param_value = self.switch_type(parameter['schema'], parameter['name'])
                        prepared_object[path][method]["parameter"].update(
                            {
                                parameter['name']: {
                                    "in": parameter['in'],
                                    "value": param_value
                                }
                            })
                    
                    # We add it outside the parameter for loop because if there parameter 
                    # has the same name as the parameter header, we will make sure
                    # the parameter header value will be replaced   
                    if self.args.header:
                        for header in self.args.header:
                            header = header.split(':')
                            prepared_object[path][method]["parameter"].update(
                                {
                                    header[0].replace(' ',''): {
                                        "in": "header",
                                        "value": header[1].replace(' ','')
                                    }
                                })

                if "requestBody" in path_object_method.keys():
                    request_body = self.get_request_body(path_object_method['requestBody'])
                    prepared_object[path][method].update(
                        {
                            "requestBody":request_body[0],
                            "contentType":request_body[1].split(';')[0]
                        }
                    )
        return prepared_object

    def server_handler(self,swagger_content):
        """
            Get a list of server URLs to use for sending requests.
        """
        servers = []

        if "servers" not in swagger_content.keys() and not self.args.server and not re.match('^https?://', self.args.target):
            print(f"{FAIL}[Error]:{ENDC} There is no server provided and no server in swagger file")
            sys.exit()

        elif "servers" in swagger_content.keys():
            if self.args.server:
                servers.append(self.args.server)
            elif self.args.all_servers:
                for server in swagger_content['servers']:
                    servers.append(server['url'])
                if self.args.server:
                    servers.append(self.args.server)
            else:
                servers.append(swagger_content['servers'][0]['url'])

        elif self.args.server: 
            servers.append(self.args.server)

        elif self.args.target and re.match("^https?://", self.args.target):
            url = parse.urlsplit(self.args.target)
            servers.append(url.scheme + '://' + url.netloc)

        return servers

    def get_content(self,swagger_content):
        """
            Extracts server and path information from the Swagger content.
        """
        if "components" in swagger_content.keys():
            self.components = swagger_content['components']
        return_preparer = {
            "server": self.server_handler(swagger_content),
            "paths": self.get_swagger_path(swagger_content)
        }

        self.swcontents = return_preparer
    
    def build_url(self,url,parameter_name,parameter_value):
        """Builds a URL with query parameters."""
        
        if "?" in url:
            url = f"{url}&{parameter_name}={parameter_value}"
        else: 
            url = f"{url}?{parameter_name}={parameter_value}"
        return url

    # Here we preper the request for sending 
    def preper_request(self,swagger_content,path,server,args):
        try: 
            for method in swagger_content:
                bodies = swagger_content[method]
                for url in server:
                    # Make a session 
                    s = requests.Session()

                    # set proxy
                    if args.proxy:
                        s.proxies.update(args.proxy)
                        
                    # Make a new request and set the method and url 
                    # we will change the url during the processing 
                    # For add parameters and if the api endpoint has argument in path 
                    # We will replace it 
                    request = requests.Request(method,str(url) + str(path)) 
                    if "parameter" in bodies.keys():
                        for parameter in bodies['parameter']:
                            parameter_body = bodies['parameter'][parameter]
                            parameter_value = parameter_body['value']
                            
                            # Add the paramters to url
                            if parameter_body['in'] == "query":
                                request.url = self.build_url(
                                    request.url,
                                    parameter,
                                    parameter_value)
                            
                            # Add headers to request
                            elif parameter_body['in'] == "header":
                                request.headers.update({parameter:str(parameter_value)})
                            
                            # Replace the api endpoint argument like 
                            # /api/v1/user/{number} we will replace {number} to correct value  
                            elif parameter_body['in'] == "path":
                                parameter_name = "(?i)\{" + parameter + "\}"
                                request.url = re.sub(parameter_name,str(parameter_value),request.url)
                            
                            else: 
                                print(f"InType {parameter_body['in']} not supported")
                    
                    # Check if the object has body for the request or not 
                    # If it has body set content-type and set the body  
                    if "requestBody" in bodies.keys():
                        request.headers.update({"Content-type":bodies['contentType']})
                
                        if bodies['contentType'] == "application/json":
                            request.json = bodies['requestBody']

                        elif bodies['contentType'] == "multipart/form-data":
                            request.files={}
                            request.data={}
                            for parameter in bodies['requestBody']:
                                if bodies['requestBody'][parameter] == "binary":
                                    request.files.update({parameter:bodies['requestBody'][parameter]})
                    
                                else:
                                    request.data.update({parameter:bodies['requestBody'][parameter]})
                        else:
                            request.data = bodies['requestBody']
                        
                    request_preper = request.prepare()
                    response = s.send(request_preper,verify=False)
                    pm(msn=4,
                        response=response,
                        path=parse.urlsplit(request.url).path,
                        method=method,
                        host=url.split('/')[2])

                    # Add this items status_code, server, request_url main object 
                    self.swcontents['paths'][path][method].update({"result":{"status":response.status_code,"server":server,"url":request.url}})
        except Exception as e:
            traceback.print_exc()
            print(e,path)

    def save_output(self, path):
        with open(path, 'w') as file_writable:
            file_writable.write(json.dumps(self.swcontents))