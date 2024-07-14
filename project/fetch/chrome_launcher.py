import  sys, os, subprocess, requests, json, psutil, time

class ChromeLauncher():

    def __init__(   self,
                    Binary      = 'chrome',
                    Hostname    = 'localhost',
                    Port        = 9222 ):

        self.Binary         =   Binary
        self.Hostname       =   Hostname
        self.Port           =   Port
        self.Process        =   None
        self.DefaultArgs    =   [
                                f' --remote-debugging-port={Port}',
                                f' --allow-insecure-localhost',
                                f' --allow-profiles-outside-user-dir',
                                f' --allow-running-insecure-content',
                                f' --silent-debugger-extension-api',
                                f' --disable-sync',
                                f' --force-devtools-available',
                                f' --no-default-browser-check',
                                f' --no-first-run',
                                f' --no-self-delete',
                                f" --remote-allow-origins='*'",
                                f" --high-dpi-support=1",
                                f" --force-device-scale-factor=1.25"
                                ]


    def Launch( self ):

        print("Launch executed")

        Counter = 0
        
        while True:

            Counter      += 1
            BrowserProcs =  [
                                Process
                                for Process in psutil.process_iter()
                                if  ( 'chrome' in Process.name() ) or
                                    ( 'msedge' in Process.name() )
                            ]

            if not BrowserProcs:
                break

            print( f'Terminating existing browser process: ' +
                   f'{BrowserProcs[0].name()} : {BrowserProcs[0].pid}' )

            try:
                BrowserProcs[0].terminate()
                BrowserProcs[0].wait()
            except:
                ...

            if Counter > 100:

                print( 'Unable to kill browsers after 100 attempts, exiting. ')
                os._exit(1)


        Command = [ self.Binary ]
        Command.extend( self.DefaultArgs )

        try:

            print()
            print( 'Launching Browser with args: ', Command )

            self.Process = subprocess.Popen( Command )

            return self.Process

        except BaseException as e:
            traceback.print_exception(e)
            return None


    def GetTargetInfo( self, TargetType = None):

        Path = None

        match TargetType:
            case 'page'     :   Path = '/json'
            case 'browser'  :   Path = '/json/version'
            case _          :   return None

        URL = f'http://{self.Hostname}:{self.Port}{Path}'

        print()
        print('GetTargetInfo: Making HTTP Request to: ' + URL)

        for x in range(10):
        
            try:

                Response    =  requests.get( url = URL )
                JSONData    =  None

                if not Response.ok:
                    print( f'Bad response code: {Response.code}' )
                else:
                    return Response.json()

            except BaseException as e:
                ...
                # traceback.print_exception(e)
                
            finally:
                print( 'Waiting for Chrome to be ready' )
                time.sleep( 2 )
                
                
        print( 'Unable to communicate with Chrome, exiting' )
        os._exit(1)


    def GetPageTargetInfo( self, PageIdx = 0 ):

        PageTargets = self.GetTargetInfo('page')

        if (( not PageTargets ) or
            ( PageIdx > ( len( PageTargets ) - 1 ))):
                return None

        for Item in PageTargets:
            print( json.dumps(Item, indent=1) )
            Item['type'] = 'page'

        return PageTargets[PageIdx]


    def GetBrowserTargetInfo( self ):

        BrowserTargetInfo           = self.GetTargetInfo('browser')

        if not BrowserTargetInfo: return None

        BrowserTargetInfo['type']   = 'browser'

        print( json.dumps(BrowserTargetInfo, indent=1) )

        return BrowserTargetInfo


