
### Overview

The Fetch game player is a Python program that communicates with the Chrome browser
to play the Fetch Gold Bar game.

It uses the Chrome CDP Protocol to locate and interact with the UI Elements of
the web page.  Communication between the test client and Chrome is done
through an asynchronous WebSocket connection.

[Official Fetch Game Instructions](https://fetch-hiring.s3.amazonaws.com/SDET/Fetch_Coding_Exercise_SDET.pdf)

[Chrome CDP Protocol Reference](https://chromedevtools.github.io/devtools-protocol/)

Before reading the details below, if you want to start with a couple of short 
videos of the game player "playing" the game:

[Video: Game Player Slow Speed](https://www.loom.com/share/fe9069c4b6a94ff3bc32c5d9eafbad5e?sid=1504cd3e-a249-48a1-8178-6e88a5b5ff43), [Video: Game Player Fast Speed](https://www.loom.com/share/31d3b34ef5864d4bbfbd85c010415804?sid=c9d79862-709b-4d0a-b4ea-497e818a4766)

Chrome CDP has a large set of functionality, much of it is very useful for 
QA Testing.  For the purposes of this small mini-project, the game player is 
only using the following CDP functions:

[Target.attachToTarget](https://chromedevtools.github.io/devtools-protocol/tot/Target/#method-attachToTarget), [Target.setAutoAttach](https://chromedevtools.github.io/devtools-protocol/tot/Target/#method-setAutoAttach), [Page.navigate](https://chromedevtools.github.io/devtools-protocol/tot/Page/#method-navigate), [Runtime.evaluate](https://chromedevtools.github.io/devtools-protocol/tot/Runtime/#method-evaluate), [Runtime.getProperties](https://chromedevtools.github.io/devtools-protocol/tot/Runtime/#method-getProperties), [Runtime.callFunctionOn](https://chromedevtools.github.io/devtools-protocol/tot/Runtime/#method-callFunctionOn), [DOM.getDocument](https://chromedevtools.github.io/devtools-protocol/tot/DOM/#method-getDocument), [DOM.requestChildNodes](https://chromedevtools.github.io/devtools-protocol/tot/DOM/#method-requestChildNodes), [DOM.describeNode](https://chromedevtools.github.io/devtools-protocol/tot/DOM/#method-describeNode), [DOM.resolveNode](https://chromedevtools.github.io/devtools-protocol/tot/DOM/#method-resolveNode), [DOM.getContentQuads](https://chromedevtools.github.io/devtools-protocol/tot/DOM/#method-getContentQuads), [Accessibility.queryAXTree](https://chromedevtools.github.io/devtools-protocol/tot/Accessibility/#method-queryAXTree), [Input.dispatchMouseEvent](https://chromedevtools.github.io/devtools-protocol/tot/Input/#method-dispatchMouseEvent), [Browser.close](https://chromedevtools.github.io/devtools-protocol/tot/Browser/#method-close)

The game player enables CDP event notifications for nearly all the CDP 
Domains, but for this small program, it is only using one of the 
async browser events: [Accessibility.loadComplete](https://chromedevtools.github.io/devtools-protocol/tot/Accessibility/#event-loadComplete)


### Installation Requirements

1.  A recent / latest version of Chrome web browser.

2.  A recent Python version: 3.11 or 3.12.

3.  The following Python packages:  **requests, websocket-client, argparse, psutil, deprecated**

There is a PyCDP python package that is bundled with the game player, and
does not need to be installed separately.

Please forgive me if I have neglected/forgotten to include any other python
requirements.

The following steps assume the user is at a command prompt interface:

1.  Unzip FetchGame.zip into a suitable location.

2.  CD into the "project" subdirectory.

3.  Run:

        python3 main.py --help

This will display the help and also verify python dependencies
are installed.  If any packages are missing it will tell you.

### Usage

The only parameter that is necessary is "--binary" which tells the game player
where to find Chrome.

For Linux:
        
        python3 main.py --binary "/usr/bin/google-chrome"

For Windows:

        python3 main.py --binary "C:\Program Files\Google\Chrome\Application\chrome.exe"

By default the game will be played 10 times in slow speed mode.

You can change the speed setting and the repeat count with the
arguments:

        python main.py --speed fast --repeat 20

You may notice the game player doesn't really "play" the game, 
because it already knows which one of the 9 buttons represents
the lowest-weight gold bar, so it chooses it immediately without
any need to weigh the bars on the scales.

The game player highlights the correct button in red color
before clicking it, so the viewer can see what the answer is
beforehand.


_
### File Summary

**main.py**

This file parses arguments and runs the game.

**fetch_game.py**

This file has most of the high-level functionality for playing the 
game, calling the CDP functions for locating elements, sending 
mouse-clicks, etc.  It has a simple Page class, Element class, 
Button class, etc.

The function that shows the overall game-flow is:  **FetchGame.Play**

**chrome_launcher.py**

This file contains a class for launching Chrome with customized parameters.
It will automatically kill any currently-running Chrome browser processes
prior to launching a new Chrome instance.

If you wish to customize the parameters used to run Chrome, they are easily
edited in the file.

**chrome_client.py**

This file provides the "engine" which communicates with Chrome. 
It establishes the WebSocket CDP connection, and provides easy-to-use 
interfaces for invoking the Chrome CDP functions and receiving async 
browser events.

**cdp_data_wrappers.py**

This file contains classes for encapsulating the response information 
from the Chrome CDP function calls and Events, to provide an easy-to-use 
interface.

**cdp**

The PyCDP classes which do the Object-To-JSON serialization + deserialization
of the CDP Protocol commands.

### END OF README

