import  sys, os, time, signal, random, json, re, websocket, ssl, queue, threading, traceback

from . import cdp
from .chrome_launcher     import ChromeLauncher
from .cdp_data_wrappers   import CDPEvent, CDPReturnValue

class ChromeClient():

    # Define + create all the core engine infrastructure
    # items such as the websocket, event queues,
    # launch the Chrome browser, and get the Target info
    # Also setup signal handler so Control-C works properly
    # to gracefully shut down Chrome and the test client
    
    def __init__( self, Launcher = None ):

        try:

            signal.signal( signal.SIGINT,   self.OSSignalHandler )
            signal.signal( signal.SIGABRT,  self.OSSignalHandler )

            self.Launcher               = Launcher
            self.WebSocket              = None
            self.SessionID              = None
            self.BrowserTargetInfo      = None
            self.PageTargetInfo         = None
            self.MessageID              = 1
            self.WebSocketReaderThread  = None
            self.EventProcessorThread   = None
            self.CommandQueue           = queue.SimpleQueue()
            self.EventQueue             = queue.SimpleQueue()
            self.PageLoadCompleteEvent  = threading.Event()

            # Launch browser

            if not self.Launcher:
                raise Exception("Failed to launch browser")

            self.BrowserProcess = self.Launcher.Launch()

            if not self.BrowserProcess:
                raise Exception("Failed to launch browser")

            # Get the Browser + Page target info from Chrome's special
            # HTTP URLs which provide the Websocket URLs for each

            self.BrowserTargetInfo  = self.Launcher.GetBrowserTargetInfo()
            self.PageTargetInfo     = self.Launcher.GetPageTargetInfo()

            if (( not self.BrowserTargetInfo )  or
                ( not self.PageTargetInfo    )):
                    raise Exception("Failed to get target info")

            # Create Page Session with Chrome

            if not self.CreateSession():
                raise Exception("Failed to create Chrome sessions")


        except BaseException as e:
            traceback.print_exception(e)
            raise


    # Signal handler for Control-C.  This will call the Chrome CDP function
    # to close the Chrome browser, then exit.
    
    def OSSignalHandler( self, Signal, Frame ):

        print(  'Caught Signal: ' +
                 f'{signal.strsignal(Signal)}' )

        if ( 'Interrupt' in signal.strsignal(Signal) ):
            self.CloseChrome()
            os._exit(0)


    # This function creates a CDP session with Chrome.
    #
    # First it connects to Chrome on the WebSocket port, 
    # then starts 2 threads.
    #
    # WebSocketReaderThread listens on the WebSocket port
    # for incoming messages from Chrome.  It can receive
    # either the results of function calls we make to
    # Chrome, or it can receive asynchronous Event messages
    # when things happen in the browser. 
    #
    # EventProcessorThread listens on the python Queue that
    # the WebSocketReaderThread delivers browser Events to.

    def CreateSession( self ):

        print("Creating Chrome Session")

        try:

            # Connect to the Page websocket URL

            if not self.Connect(
                    URL = self.PageTargetInfo.get( 'webSocketDebuggerUrl' )):
                        return False

            # Start MessageReader thread

            self.StartWebSocketReader()

            # Start EventProcessor thread

            self.StartEventProcessor()

            # Execute the CDP command to attach to the Page target

            ReturnValue =   self.ExecuteMethod(
                                cdp.target.attach_to_target,
                                target_id   =   cdp.target.TargetID(
                                                self.PageTargetInfo['id'] ),
                                flatten     =   True )

            self.SessionID  = ReturnValue.CDPObject

            if not self.SessionID:
                print("Failed to get SessionID")
                return False

            # Execute CDP command to auto-attach to new Pages
            
            ReturnValue     =   self.ExecuteMethod(
                                cdp.target.set_auto_attach,
                                    auto_attach = True,
                                    flatten     = True,
                                    wait_for_debugger_on_start = True )

            # ReturnValue.Print()
            return True

        except:
            raise


    
    # This function connects to Chrome on a WebSocket port
    
    def Connect( self, URL ):

        SSLOptions = {  'cert_reqs'      : ssl.CERT_NONE,
                        'check_hostname' : False }

        try:

            self.WebSocket  = websocket.WebSocket(
                                sslopt              = SSLOptions,
                                enable_multithread  = True )

            self.WebSocket.connect( URL,
                                    suppress_origin = True )

            if not self.WebSocket.connected:
                return False

            print( f"Connected To: {URL}" )

            return True

        except:
            raise



    def ExecuteMethod( self, CDPMethod, **kwargs ):

        # This function calls a Chrome CDP method and returns
        # the response.

        # The functions in the Chrome CDP package accept Python
        # objects that represent the Chrome CDP data models,
        # and provide Python generators which convert Python objects
        # to Python / JSON format for wire transfer.

        # The way it works is you call the Python generators twice:
        #
        # First to convert the Chrome CDP Object to serializable JSON.
        #
        # Then a 2nd time to convert the Chrome Response from JSON
        # into a Python object.
        #
        # ...
        #
        # Call the CDP method to get the Python generator for
        # the command, initializing it with all the args for the call.

        Generator       = CDPMethod( **kwargs )

        # Next, invoke the generator which returns a dictionary
        # representing the Chrome CDP function call / command.
        # Note:  send(None) is the same as next()

        ChromeMethod    = Generator.send( None )

        # Now send the command to Chrome via WebSocket connection

        Response        = self.SendCommand( ChromeMethod )

        # Create a ReturnValue container to keep the response in
        # various formats

        ReturnValue     = CDPReturnValue( ChromeMethod, Response )

        if ReturnValue == None:
            print( 'Critical failure creating CDPReturnValue' )
            return None

        if ReturnValue.Error != None:
            print( 'Received Error/Exception from CDP Protocol' )
            ReturnValue.PrintError()
            return ReturnValue

        if ReturnValue.Result == None:
            print( 'Critical failure, CDPReturnValue.Result is None' )
            return ReturnValue


        # The JSON response is stored in ReturnValue.Result.
        #
        # To deserialize it into a Python object with the Chrome CDP
        # package, call the Python generator a second time.
        #
        # The generator delivers the deserialized Python response object
        # by raising a StopIteration exception, for which it adds the
        # deserialized Python object as an *attribute* of the StopIteration
        # Exception itself. It's kind of weird but that's the way the CDP package works.
        #
        # We store the deserialized CDP object in the ReturnValue container.

        if ReturnValue.Result != {}:

            try:

                Generator.send( ReturnValue.Result )

                # Note: Some of the CDP return values
                # turn into Tuples after conversion to
                # Python objects.
                # Sometimes 2, 3 or 4 values depending
                # on the API call.

            except StopIteration as GeneratorResult:
                ReturnValue.CDPObject = GeneratorResult.value

            if ReturnValue.CDPObject == None:
                print('Failed to convert Result into CDPObject')
                ReturnValue.PrintResponse()
                return None

        return ReturnValue


    # This function remotely executes any arbitrary JavaScript 
    # function on any live JavaScript object that exists inside 
    # of the Chrome browser.  It's pretty awesome.
    
    def ExecuteFunctionOn(  self,
                            function_declaration = None,
                            object_id = None,
                            arguments = None,
                            execution_context_id = None,
                            return_by_value = True ):

        ReturnValue = None

        if ( execution_context_id ):

            ReturnValue = self.ExecuteMethod(
                cdp.runtime.call_function_on,
                function_declaration = function_declaration,
                execution_context_id = execution_context_id,
                arguments = arguments,
                silent = False,
                return_by_value = return_by_value,
                generate_preview = False,
                user_gesture = True,
                await_promise = True,
                throw_on_side_effect = False,
                object_group = "mygroup" )

        elif ( object_id ):

            ReturnValue = self.ExecuteMethod(
                cdp.runtime.call_function_on,
                function_declaration = function_declaration,
                object_id = object_id,
                arguments = arguments,
                silent = False,
                return_by_value = return_by_value,
                generate_preview = False,
                user_gesture = True,
                await_promise = False,
                throw_on_side_effect = False,
                object_group = "mygroup" )

        return ReturnValue


    # This function remotely executes any arbitrary JavaScript
    # that you supply it, in the global "window" execution context.
    # or a custom context.  It is pretty awesome.
    
    def ExecuteScript(  self, expression      = None, 
                              return_by_value = False, 
                              context_id = 1 ):

        ReturnValue = self.ExecuteMethod(
            cdp.runtime.evaluate,
            expression                        = expression,
            object_group                      = "mygroup",
            return_by_value                   = return_by_value,
            #context_id                        = cdp.runtime.ExecutionContextId(context_id),
            include_command_line_api          = True,
            silent                            = False,
            generate_preview                  = False,
            user_gesture                      = True,
            await_promise                     = False,
            throw_on_side_effect              = False,
            timeout                           = cdp.runtime.TimeDelta(60000),
            disable_breaks                    = True,
            repl_mode                         = True,
            allow_unsafe_eval_blocked_by_csp  = True)

        return ReturnValue


    # This is the EventProcessor thread.  It listens for
    # Chrome CDP browser events, or custom DOM events.
    # If requested, it will signal an interested client that
    # it received a particular browser event.
    
    # We're currently not acting upon very much, only the
    # LoadComplete event.
    
    def EventProcessor( self ):

        print('EventProcessor: Started')

        EventMessage = None

        try:

            while True:

                EventMessage  =  CDPEvent( self.EventQueue.get() )

                # print()
                # print( 'EventProcessor: Got event: ', type( EventMessage.CDPObject ))
                # EventMessage.PrintMessage()

                match type( EventMessage.CDPObject ):

                    case cdp.accessibility.LoadComplete:

                        #EventMessage.PrintMessage()

                        Result = self.ExecuteMethod( cdp.dom.get_document,
                                                     depth = -1, pierce = True )

                        Result = self.ExecuteMethod( cdp.dom.request_child_nodes,
                                                     node_id = cdp.dom.NodeId( 0 ),
                                                     depth = -1, pierce = True   )

                        # print("Event Processor: Setting PageLoadCompleteEvent")
                        self.PageLoadCompleteEvent.set()

                    case cdp.page.JavascriptDialogOpening:
                        
                        ReturnValue = self.ExecuteMethod( 
                                cdp.input_.dispatch_key_event,
                                type_       = 'keyDown',
                                key         = 'Enter',                                
                                timestamp   = cdp.input_.TimeSinceEpoch( time.time() ))
                        
                    
                    case cdp.runtime.ConsoleAPICalled:
                        EventMessage.PrintMessage()


        except BaseException as e:
            traceback.print_exception(e)


    # This is the WebSocketMessageReader thread, which
    # receives all the messages from Chrome, and adds them to 
    # either the CommandQueue (for function call results), or
    # the EventQueue (for browser events)
    
    def WebSocketMessageReader( self ):

        try:

            while True:

                Opcode = Frame = Message = None

                # Block until a websocket message tuple arrives

                ( Opcode,
                  Frame, )  = self.WebSocket.recv_data( control_frame = False )

                # Process the message

                match Opcode:

                    case websocket.ABNF.OPCODE_TEXT:

                        # Load the text message as a JSON dictionary

                        Message = json.loads( Frame.decode('utf-8') )

                        # If there is an 'id' value, it means it is
                        # the result of a CDP function call command.

                        # If not, it is an async CDP event.

                        if Message.get( 'id' ) != None:

                            # Send the message to the Command queue
                            self.CommandQueue.put( Message )

                        else:

                            # Send the message to the Event queue
                            self.EventQueue.put( Message )


                    # Various other WebSocket opcodes that might happen
                    # Adding for completeness

                    case websocket.ABNF.OPCODE_CONT:
                        print()
                        print( 'Control Frame Received:' )
                        print( Frame )
                        print()
                    case websocket.ABNF.OPCODE_BINARY:
                        print()
                        print( 'Binary Frame Received')
                        print()
                    case websocket.ABNF.OPCODE_CLOSE:
                        print()
                        print( 'Close Frame Received' )
                        print()
                    case websocket.ABNF.OPCODE_PING:
                        print()
                        print( 'Ping Frame Received' )
                        print( Frame )
                        print()
                    case websocket.ABNF.OPCODE_PONG:
                        print()
                        print( 'Pong Frame Received' )
                        print( Frame )
                        print()
                    case _:
                        print()
                        print( 'Unknown Opcode Received' )
                        print( Frame )
                        print()

        except websocket._exceptions.WebSocketConnectionClosedException as wsce:
            print( 'MessageReader: Browser connection is closed' )
        except BaseException as e:
            traceback.print_exception(e)

        os._exit( 1 )


    # This function sends a CDP Commmand (function call) to 
    # the Chrome browser via the WebSocket connection.
    #
    # After sending the command (calling the function),
    # then it waits for the response to show up in the CommandQueue
    
    def SendCommand( self, Command ):

        try:

            # If we got a string, load it as a JSON dictionary

            if isinstance( Command, str):
                Command = json.loads( Command )

            # Each command needs to have a unique ID
            # so we use an incrementing integer value

            self.MessageID += 1
            Command['id'] = self.MessageID

            # Add the SessionID
            if self.SessionID:
                Command['sessionId'] = self.SessionID

            # Serialize command to a JSON string to send it to Chrome via websocket
            Command = json.dumps( Command )

            # Send the JSON to the WebSocket connection
            self.WebSocket.send( Command,
                                 opcode = websocket.ABNF.OPCODE_TEXT )


            # The response arrives asychronously, and is
            # read by the WebSocketReaderThread, which
            # sends it here via the CommandQueue.

            Response = self.CommandQueue.get( block = True )

            return Response

        except BaseException as e:
            traceback.print_exception(e)
            raise


    # Starts the WebSocketReader thread
    
    def StartWebSocketReader( self ):

        try:

            self.WebSocketReaderThread = threading.Thread(
                                         target = self.WebSocketMessageReader,
                                         daemon = True )

            self.WebSocketReaderThread.start()

            return True

        except BaseException as e:
            traceback.print_exception(e)
            raise


    # Starts the EventProcessor thread
    
    def StartEventProcessor( self ):

        try:

            self.EventProcessorThread = threading.Thread(
                                        target = self.EventProcessor,
                                        daemon = True )

            self.EventProcessorThread.start()

        except BaseException as e:
            traceback.print_exception(e)
            raise


    # Waits for a Python Event object to be signaled
    
    def WaitForEvent( self, Event, Timeout = None ):

        if not Event: return False
        Event.clear()
        return Event.wait( Timeout )


    # Sends the command to Chrome to close the browser.
    
    def CloseChrome( self ):

        ReturnValue = self.ExecuteMethod( cdp.browser.close )
        ReturnValue.Print()
        
        
