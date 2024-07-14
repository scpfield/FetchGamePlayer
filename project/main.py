import  sys, argparse
from    fetch.fetch_game import FetchGame

if __name__ == '__main__':

    ArgParser = argparse.ArgumentParser( 
                    argument_default    = True,
                    add_help            = True,
                    description         = 'FetchGame')

    ArgGroup  = ArgParser.add_argument_group()

    ArgGroup.add_argument( 
        '--binary',
        required    = True,
        action      = 'store',
        default     = 'chrome',
        help        = ( 'Full path + filename to the chrome or msedge binary, ' +
                        'or simply the filename if it exists in $PATH. ' +
                        'Default = "chrome". ' +
                        'On linux it is likely named named: "google-chrome"' ))

    ArgGroup.add_argument(  
        '--hostname',
        required    = False,
        action      = 'store',
        default     = 'localhost',
        help        = ( 'Hostname for Chrome to bind its WebSocket port. ' +
                        'Default = localhost' ))

    ArgGroup.add_argument(  
        '--port',
        required    = False,
        action      = 'store',
        type        = int,
        default     = 9222,
        help        = 'Listener port for Chrome.  Default = 9222' )

    ArgGroup.add_argument(  
        '--speed',
        required    = False,
        action      = 'store',
        default     = 'slow',
        help        = ( 'Speed of automation. ' +
                        'Values either "fast" or "slow". ' + 
                        'Default = "slow"' ))

    ArgGroup.add_argument(  
        '--repeat',
        required    = False,
        action      = 'store',
        type        = int,
        default     = 10,
        help        = 'Repeat count. Default is 10.' )

    print()
    
    Args    = ArgParser.parse_args()
    
    Game    = FetchGame( 
                     Speed      = Args.speed,
                     Repeat     = Args.repeat,
                     Binary     = Args.binary,
                     Hostname   = Args.hostname,
                     Port       = Args.port )

    Game.Play()
    Game.CloseChrome()
    
    exit( 0 )


