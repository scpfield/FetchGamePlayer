import  sys, os, time, signal, random, json, re, copy
from . import cdp

class CDPReturnValue():

    def __init__( self, Command, Message ):

        try:

            self.Message    = Message
            self.Command    = Command

            self.ID         = self.Message.get( 'id' )
            self.Method     = self.Message.get( 'method' )
            self.Result     = self.Message.get( 'result' )
            self.Params     = self.Message.get( 'params' )
            self.Error      = self.Message.get( 'error' )
            self.CDPObject  = None

            if self.Result:
            
                ExceptionDetails = self.Result.get( 'exceptionDetails' )
                
                if ExceptionDetails:
                    if not self.Error:
                        self.Error = {}
                        self.Error['exceptionDetails'] = ExceptionDetails
                    else:
                        self.Error['exceptionDetails'] = ExceptionDetails
                        
                ErrorText = self.Result.get( 'errorText' )
                
                if ErrorText:
                    if not self.Error:
                        self.Error = {}
                        self.Error['errorText'] = ErrorText
                    else:
                        self.Error['errorText'] = ErrorText
                

        except BaseException as e:
            traceback.print_exception(e)

    def IsError( self ):
        return True if self.Error != None else False

    def PrintObject( self ):
        print()
        print( 'Object:' )
        print( str(self.CDPObject) )

    def PrintMessage( self ):
        print()
        print( 'Message:' )
        print( json.dumps( self.Message, indent = 2 ))

    def PrintResult( self ):
        print()
        print( 'Result:' )
        print( json.dumps( self.Result, indent = 2 ))

    def PrintCommand( self ):
        print()
        print( 'Command:' )
        print( json.dumps( self.Command, indent = 2 ))

    def PrintError( self ):
        print()
        print( 'Error:' )
        print( json.dumps( self.Error, indent = 2 ))

    def Print( self ):

        self.PrintCommand()
        self.PrintMessage()
       
    def __str__( self ):
        if self.Message:
            return( json.dumps( self.Message, indent = 2 ))

    def __len__( self ):
        if self.Message:
            return( len( json.dumps( self.Message, indent = 2 )))

    def __getitem__(self, Index):
        if self.Message:
            return( json.dumps( self.Message, indent = 2 )[Index])

    def __bool__( self ):
        if self.Error:   return False
        else:            return True




class CDPEvent():

    def __init__(self, Message):

        self.Message         = Message
        self.Method          = self.Message.get( 'method' )
        self.Result          = self.Message.get( 'result' )
        self.Params          = self.Message.get( 'params' )
        self.Error           = self.Message.get( 'error'  )
        self.Args            = self.Message.get( 'args'   )

        self.CDPObject              = None
        self.DOMEventObjectID       = None
        self.DOMEventTargetObjectID = None
        self.DOMEventDetail         = None
        self.DOMEventTargetDetail   = None

        # This is a CDP package utility function that parses
        # a CDP event string into a CDP object

        # fix for one of their bugs:
        if self.Method == 'Animation.animationStarted':
            Animation = self.Params.get('animation')
            if Animation:
                Source = Animation.get('source')
                if Source:
                    Iterations = Source.get('iterations')
                    if Iterations == None:
                        Source['iterations'] = 0

        try:
            self.CDPObject      = cdp.util.parse_json_event( self.Message )
        except BaseException as e:
            traceback.print_exception(e)
            os._exit(0)


    def ParseDOMEventObjects( self ):

        if type( self.CDPObject ) != cdp.runtime.ConsoleAPICalled:
            return False

        if not self.Params: return False

        Args = self.Params.get('args')

        if ( Args ) and ( len(Args) > 2 ):

            self.DOMEventObjectID        = Args[1].get( 'objectId' )
            self.DOMEventTargetObjectID  = Args[2].get( 'objectId' )


    def GetDOMEventDetails(self, ExecuteMethod, SendCommand ):

        if not self.DOMEventDetail:

            ObjectID =  cdp.runtime.RemoteObjectId(
                        self.DOMEventObjectID)

            self.DOMEventDetail = ExecuteMethod(
                cdp.runtime.get_properties,
                object_id = ObjectID,
                own_properties = False,
                accessor_properties_only = False,
                generate_preview = False,
                non_indexed_properties_only = False )

            # self.DOMEventDetail.Print()

        if not self.DOMEventTargetDetail:

            ObjectID =  cdp.runtime.RemoteObjectId(
                        self.DOMEventTargetObjectID)

            self.DOMEventTargetDetail = ExecuteMethod(
                cdp.runtime.get_properties,
                object_id = ObjectID,
                own_properties = False,
                accessor_properties_only = False,
                generate_preview = False,
                non_indexed_properties_only = False )

            # self.DOMEventTargetDetail.Print()


    def ParseDOMEventSummary( self ):

        if type( self.CDPObject ) != cdp.runtime.ConsoleAPICalled:
            return False

        DOMEvent =  self.Message

        if not self.Params: return False

        EventItems      = [ 'DOMEventType', 'TargetProto', 'TargetName',
                            'TargetTagName', 'TargetClassName',
                            'EventMessage', 'EventError', 'TargetText' ]

        for EventItem in EventItems:

            EventValue  =  [  PropItem.get      ( 'value'   )
                              if   DOMEvent.get ( 'params'  ) else [ {} ]
                              for  ArgItem      in DOMEvent.get( 'params'  ).get( 'args' )
                              if   ArgItem.get  ( 'preview' )
                              for  PropItem     in ArgItem.get ( 'preview' ).get( 'properties' )
                              if   PropItem.get ( 'name'    )  == EventItem ]

            EventValue  = EventValue[0] if EventValue else ''
            EventValue  = EventValue.strip().replace('\n', '').strip(' ').strip('"')
            EventValue  = re.sub(' +', ' ', EventValue)
            EventValue  = re.sub('\t+', ' ', EventValue)

            if (( EventValue == 'undefined' ) or
                ( EventValue == 'null' )):
                EventValue = ''

            if EventItem == 'EventMessage' and EventValue:
                EventValue = unquote(EventValue)

            setattr( self, EventItem, EventValue )

        return True

    def GetCDPEventDetails( self, ExecuteMethod, SendCommand ):

        match type(self.CDPObject):
            case cdp.dom.ChildNodeInserted:
                MessageCopy = copy.deepcopy(self.Message)
                #self.PrintMessage()
                ParentNodeID = MessageCopy.get('params').get('parentNodeId')
                PreviousNodeID = MessageCopy.get('params').get('previousNodeId')
                NodeID = MessageCopy.get('params').get('node').get('nodeId')
                BackendNodeID = MessageCopy.get('params').get('node').get('backendNodeId')

                ReturnValue = ExecuteMethod(
                                  cdp.dom.describe_node,
                                  backend_node_id = cdp.dom.BackendNodeId(ParentNodeID),
                                  depth = -1,
                                  pierce = True )
                #ReturnValue.Print()

                ReturnValue = ExecuteMethod(
                                  cdp.dom.describe_node,
                                  backend_node_id = cdp.dom.BackendNodeId(PreviousNodeID),
                                  depth = -1,
                                  pierce = True )
                #ReturnValue.Print()

                ReturnValue = ExecuteMethod(
                                  cdp.dom.describe_node,
                                  backend_node_id = cdp.dom.BackendNodeId(BackendNodeID),
                                  depth = -1,
                                  pierce = True)
                #ReturnValue.Print()

                ReturnValue = ExecuteMethod(
                                  cdp.dom.resolve_node,
                                  node_id = cdp.dom.NodeId(ParentNodeID),
                                  #backend_node_id = cdp.dom.BackendNodeId(BackendNodeID),
                                  object_group = 'ABCD')
                #ReturnValue.Print()



    def PrintObject( self ):
        print(str(self.CDPObject))

    def PrintMessage( self ):
        print( json.dumps( self.Message, indent = 2 ))

    def PrintEvent( self ):
        print(type(self.CDPObject))
        print(self.CDPObject)

    def __str__( self ):
        if self.Message:
            return( json.dumps( self.Message ))

    def __len__( self ):
        if self.Message:
            return( len( json.dumps( self.Message )))

    def __getitem__(self, Index):
        if self.Message:
            return( json.dumps( self.Message )[Index])
    ...


