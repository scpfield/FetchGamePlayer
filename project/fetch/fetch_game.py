import  sys, os, time, random, json, argparse

from  .chrome_launcher   import ChromeLauncher
from  .chrome_client     import ChromeClient
from  .                  import cdp

class FetchGame():

    def __init__(   self, 
                    Speed    = 'slow',
                    Repeat   = 10,
                    Binary   = None,
                    Hostname = None,
                    Port     = None ):

        self.Speed  = Speed
        self.Repeat = Repeat
        
        Launcher    = ChromeLauncher( 
                        Binary      = Binary,
                        Hostname    = Hostname,
                        Port        = Port )
                        
        self.CDP    = ChromeClient( 
                        Launcher  = Launcher )
        
        if not self.InitializeCDP():
            raise Exception( 'Failed to initialize CDP' )


    def Play( self ):
        
        # Create a Page object for the URL
        Page = FetchGamePage( 'http://sdetchallenge.fetch.com/', 
                               self.CDP )
    
        if not Page: return False

        # Play the game X number of times
        for x in range( self.Repeat ):

            # Navigate to the page
            if not Page.NavigateToPage():
                print( f'Failed to navigate to the game page' )
                return False
            
            # Initialize our page element objects
            if not Page.InitializeElements():
                print( f'Failed to initialize')
                return False
            
            # Iterate the list of 9 buttons and find out which
            # one represents the lowest-weight gold bar.
            # Then, click the button to display the window.alert
            
            for Button in [ Page.Button0, Page.Button1, Page.Button2,
                            Page.Button3, Page.Button4, Page.Button5,
                            Page.Button6, Page.Button7, Page.Button8 ]:
                
                # Retrieve the button's data-value attribute
                DataValue = Button.GetAttribute( 'data-value' )
                
                # Need to make it an integer
                try:
                    DataValue = int( DataValue )
                except:
                    print( f'Failed to convert {DataValue} to integer' )
                    return False
                    
                # If mod 2 = 0, it is the correct button
                if DataValue % 2 == 0:
                    
                    print( f'The correct gold bar is: {Button.Name}' )

                    # Set a highlight color on the button so the user
                    # can see which button is going to be clicked
                    
                    Button.SetAttribute( 'style', 'background-color:red;color:white' )
                                        
                    # Pause for a second if we're in slow speed mode
                    if self.Speed == 'slow':
                        time.sleep(1)

                    # Send the click event to the button                    
                    print( f'Clicking button: {Button.Name}' )
                    Button.Click()
                    
                    # Regardless of speed setting, we have to pause
                    # just a tiny bit after clicking the button,
                    # or else the window.alert disappears too quickly
                    time.sleep(0.05)
                    
                    # Pause for a second if we're in the slow speed mode
                    if self.Speed == 'slow':
                        time.sleep(1)

                    # We found the correct button, so break early
                    break
                    
            else:
                # I have never seen this happen, but just in case
                print( f'None of the buttons have the correct answer')
                return False
            
            # Game is over.  Do it again maybe.
            print('Game over')


    def CloseChrome( self ):
        self.CDP.CloseChrome()
        
    def InitializeCDP( self ):

        ReturnValue = self.CDP.ExecuteMethod( cdp.log.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.page.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.page.set_lifecycle_events_enabled, 
                                              enabled = True )
        ReturnValue = self.CDP.ExecuteMethod( cdp.dom.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.dom_snapshot.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.dom_storage.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.debugger.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.runtime.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.css.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.accessibility.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.audits.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.inspector.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.overlay.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.profiler.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.performance.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.service_worker.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.layer_tree.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.media.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.console.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.database.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.animation.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.indexed_db.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.heap_profiler.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.security.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.web_authn.enable )
        ReturnValue = self.CDP.ExecuteMethod( cdp.browser.get_version )
        ReturnValue.Print()
        return True
        

class FetchGamePage():

    def __init__( self, URL, CDP ):

        self.URL                = URL
        self.CDP                = CDP
        self.Button0            = None
        self.Button1            = None
        self.Button2            = None
        self.Button3            = None
        self.Button4            = None
        self.Button5            = None
        self.Button6            = None
        self.Button7            = None
        self.Button8            = None
    
    
    def NavigateToPage( self ):

        if not self.URL: return False
        if not self.CDP: return False
        
        ReturnValue = self.CDP.ExecuteMethod( cdp.page.navigate,
                                              url = self.URL )
        
        if ReturnValue.Error: return False
        
        self.CDP.WaitForEvent( self.CDP.PageLoadCompleteEvent )

        ReturnValue = self.CDP.ExecuteMethod( cdp.dom.get_document,
                                              depth  = -1, 
                                              pierce = True )

        if ReturnValue.Error: return False
        
        self.DocumentNode = ReturnValue.CDPObject

        ReturnValue = self.CDP.ExecuteMethod( cdp.dom.request_child_nodes,
                                              node_id = self.DocumentNode.node_id,
                                              depth   = -1, 
                                              pierce  = True )

        if ReturnValue.Error: return False
        
        return True
        

    def InitializeElements( self ):

        self.Button0    = Button(  Name     = '0',
                                   Locator  = { 'name' : '0', 'role' : 'button' },
                                   CDP      = self.CDP )
                                    
        self.Button1    = Button(  Name     = '1',
                                   Locator  = { 'name' : '1', 'role' : 'button' },
                                   CDP      = self.CDP )
                                   
        self.Button2    = Button(  Name     = '2',
                                   Locator  = { 'name' : '2', 'role' : 'button' },
                                   CDP      = self.CDP )

        self.Button3    = Button(  Name     = '3',
                                   Locator  = { 'name' : '3', 'role' : 'button' },
                                   CDP      = self.CDP )

        self.Button4    = Button(  Name     = '4',
                                   Locator  = { 'name' : '4', 'role' : 'button' },
                                   CDP      = self.CDP )

        self.Button5    = Button(  Name     = '5',
                                   Locator  = { 'name' : '5', 'role' : 'button' },
                                   CDP      = self.CDP )

        self.Button6    = Button(  Name     = '6',
                                   Locator  = { 'name' : '6', 'role' : 'button' },
                                   CDP      = self.CDP )

        self.Button7    = Button(  Name     = '7',
                                   Locator  = { 'name' : '7', 'role' : 'button' },
                                   CDP      = self.CDP )

        self.Button8    = Button(  Name     = '8',
                                   Locator  = { 'name' : '8', 'role' : 'button' },
                                   CDP      = self.CDP )
        
        return True
                    

class Element():

    def __init__(   self,
                    Name    = None,
                    Label   = None,
                    Locator = None,
                    CDP     = None  ):

        self.Locator    = Locator
        self.Name       = Name
        self.NodeID     = None
        self.ObjectID   = None
        self.CDP        = CDP
        self.Label      = Label if Label else Name

        # Coordinates to land clicks on
        self.UpperLeft  = ( None, None )
        self.UpperRight = ( None, None )
        self.LowerRight = ( None, None )
        self.LowerLeft  = ( None, None )
        self.Center     = ( None, None )


    def Locate( self ):

        ReturnValue     = self.CDP.ExecuteMethod( cdp.dom.get_document,
                                                  depth = 1, pierce = True )

        if ReturnValue.Error: return False

        DocumentNode    = ReturnValue.CDPObject

        ReturnValue     = self.CDP.ExecuteMethod( cdp.accessibility.query_ax_tree,
                                node_id         = DocumentNode.node_id,
                                accessible_name = self.Locator.get( 'name' ),
                                role            = self.Locator.get( 'role' ))

        if ReturnValue.Error: return False

        if not ReturnValue.Result.get('nodes'): return False

        self.NodeID     = ReturnValue.Result.get('nodes')[0].get('nodeId')

        ReturnValue     = self.CDP.ExecuteMethod( cdp.dom.resolve_node,
                                                  backend_node_id = cdp.dom.NodeId( self.NodeID ))

        if ReturnValue.Error: return False

        self.ObjectID   = ReturnValue.Result.get('object').get('objectId')

        if not self.GetContentQuads(): return False

        return True


    def GetAttribute( self, Name ):

        if not self.Locate():   self.Located = False
        else:                   self.Located = True

        if not self.Located: return False
                
        FunctionDeclaration = (
            f"function(Name) {{ return this.getAttribute('{Name}'); }}" )
            
        FunctionArgument    = cdp.runtime.CallArgument( Name )
        
        ReturnValue = self.CDP.ExecuteFunctionOn(
                        object_id = cdp.runtime.RemoteObjectId( self.ObjectID ),
                        function_declaration = FunctionDeclaration,
                        arguments = [ FunctionArgument ] )
                        
        
        AttributeValue = ReturnValue.Result.get('result').get('value')

        return AttributeValue


    def SetAttribute( self, Name, Value ):

        if not self.Locate():   self.Located = False
        else:                   self.Located = True

        if not self.Located: return False
                
        FunctionDeclaration = (
            f"function(Name, Value) {{ return this.setAttribute('{Name}', '{Value}'); }}" )
            
        FunctionArgument1    = cdp.runtime.CallArgument( Name )
        FunctionArgument2    = cdp.runtime.CallArgument( Value)
        
        ReturnValue = self.CDP.ExecuteFunctionOn(
                        object_id = cdp.runtime.RemoteObjectId( self.ObjectID ),
                        function_declaration = FunctionDeclaration,
                        arguments = [ FunctionArgument1, FunctionArgument2 ] )
            
        AttributeValue = ReturnValue.Result.get('result').get('value')

        return AttributeValue

        
    def GetContentQuads( self ):

        ReturnValue     = self.CDP.ExecuteMethod(
                            cdp.dom.get_content_quads,
                            object_id = cdp.runtime.RemoteObjectId( self.ObjectID ))

        if ReturnValue.Error: return False

        Quads           = ReturnValue.Result.get( 'quads' )[0]

        self.UpperLeft  = ( Quads[0], Quads[1] )
        self.UpperRight = ( Quads[2], Quads[3] )
        self.LowerRight = ( Quads[4], Quads[5] )
        self.LowerLeft  = ( Quads[6], Quads[7] )

        CenterX    = self.UpperLeft[0]  + (( self.UpperRight[0] - self.UpperLeft[0]  ) / 2 )
        CenterY    = self.LowerRight[1] + (( self.UpperRight[1] - self.LowerRight[1] ) / 2 )

        self.Center = ( CenterX, CenterY )

        return True


class Button( Element ):

    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )

    def Click( self, Speed = None ):

        if not self.Locate():   self.Located = False
        else:                   self.Located = True

        if not self.Located: return False

        ReturnValue = self.CDP.ExecuteMethod( cdp.input_.dispatch_mouse_event,
                                              type_       = 'mousePressed',
                                              x           = self.Center[0],
                                              y           = self.Center[1],
                                              button      = cdp.input_.MouseButton(
                                                            cdp.input_.MouseButton.LEFT ),
                                              buttons     = 1,
                                              click_count = 1,
                                              timestamp = cdp.input_.TimeSinceEpoch( time.time() ))

        if ReturnValue.Error: return False

        ReturnValue = self.CDP.ExecuteMethod( cdp.input_.dispatch_mouse_event,
                                              type_       = 'mouseReleased',
                                              x           = self.Center[0],
                                              y           = self.Center[1],
                                              button      = cdp.input_.MouseButton(
                                                            cdp.input_.MouseButton.LEFT ),
                                              buttons     = 1,
                                              click_count = 1,
                                              timestamp = cdp.input_.TimeSinceEpoch( time.time() ))

        if ReturnValue.Error: return False
        
        return True

