# handy
Hand API

## Setup

This project contains two separate Python3 Flask web apps. 
Each web app is contained in it's own subdirectory of `src`. 
Every `src` subdirectory contains a `requirement.txt` text file which can be used to install dependencies using
`python3 -m pip install -r requirements.txt`. 
This command may be different or require extra permissions depending on your Python install and your OS. 

Once dependencies have been installed, all Flask webapps can be run with `python3 -m flask run -h <IP>`. 
A custom port number (default: 5000) can be set using the `-p` flag.

## Source Code

`api` is the hand API. 
This is the main back-end interface. 
This uses the `picamera` Python lib to interact with a connected Pi Camera, so this should be run on a Raspberry Pi. 
Handy's API relies on the `hand_analysis` web app to get hand wireframes from pictures. 
By default, the hand API uses the cloud-hosted `hand_analysis` instance at http://handy.zettagram.com but this can be modified by modifying the URL in `src/api/fingers.py`. 
All API endpoints are defined in the Hand API Spec document: https://docs.google.com/document/d/1Rw9L3evGnwixczuN0MaCeNYR2s6Sh1c_muZcxsOI2BM/edit?usp=sharing 

`hand_analysis` is the machine learning endpoint. 
If you wish to use a custom instance of `hand_analysis`, run this Flask webapp and perform the necessary modifications to the `api` webapp. 
This endpoint is undocumented since it should not be directly accessed. 

`tools` contains scripts for common and repetitive tasks, such as automatically processing images through the Handy API. 
These are not guaranteed to be stable or to even work. 

# LICENSE

This project is licensed under the GNU GPLv3 https://github.com/CEG4912capstone/handy/blob/main/LICENSE
