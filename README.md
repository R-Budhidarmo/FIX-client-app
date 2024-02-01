# FIX Client Application

This FIX (Financial Information eXchange) client application serves as a proof-of-concept (POC) trading communication system that exchanges data with a remote FIX server. **Note:** *The code was initially developed as part of a job interview to meet the specifications set by the interviewer. Feel free to fork it & modify it as you like, but be careful with some of the details (e.g. config & xml files). Make sure they're set according to your specific needs).*
<br>
<br>This code was developed using Python 3.9.12 and leverages a known open-source [QuickFIX engine](https://quickfixengine.org/) library to handle FIX protocol messaging. For this particular example, FIX version 4.2 was used. The code was designed for a client / initiator to send new orders, cancel existing orders, as well as receive execution reports and key trade statistics at the end. 

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Application Design](#application-design)
- [How the Application Works](#how-the-application-works)

---

## Installation

To run the Fapplication, you need to have Python 3.x installed (as mentioned above, Python 3.9.12 was used during development). Several Python 3 standard modules were employed: ```system```, ```random```, ```argparse```, ```time```, and ```datetime```. In addition to the standard libraries, [```QuickFIX```](https://pypi.org/project/quickfix/) version 1.15.1 and [```pandas```](https://pypi.org/project/pandas/1.4.2/) version 1.4.2 can be installed as follows:

```bash
pip install quickfix
pip install pandas==1.4.2
```
or simply:
```bash
pip install -r requirements.txt
```
---

## Configuration

The configuration is specified in the `configfile.cfg` file (also shown below). This file contains the settings for the FIX session, such as connection details, session parameters, and file paths for logging and storing messages.

```ini
[DEFAULT]
ConnectionType=initiator
StartTime=00:00:00
EndTime=00:00:00
HeartBtInt=30
ReconnectInterval=60
FileStorePath=./store/
FileLogPath=./log/
ValidateFieldsHaveVal=N
ValidateUserDefinedFields=N
ValidateFieldsOutOfOrder=N
UseDataDictionary=Y
DataDictionary=./spec/FIX42_DTL.xml
RefreshOnLogon=N
ResetOnLogon=Y
PersistMessages=N

[SESSION]
SessionID=DTL_TEST
BeginString=FIX.4.2
SocketConnectHost=129.126.125.251
SocketConnectPort=5100
SenderCompID=OPS_CANDIDATE_9_2308
TargetCompID=DTL
```

The configuration settings can be adjusted according to your server specifications. For further information, refer to the QuickFIX engine [documentation](https://quickfixengine.org/c/documentation/).

---

## Usage

To run the FIX client application, execute the `client.py` script from the command line. You can provide a custom configuration file using the `-c` option:

```bash
python client.py -c configfile.cfg
```
Alternatively, the following worked as well:

```bash
python client.py
```

Follow the prompts to interact with the application, either to send new orders or to exit the application.

---

## Application Design

The application consists of two files: `client.py` and `application.py`. The `client.py` script initializes the FIX session and starts the application, while the `application.py` script defines the behavior of the FIX application.

### `client.py`

This script starts up the FIX session using the provided configuration file. It creates an instance of the `MyApp` class, which is defined in `application.py`. The application's main loop can then be run to handle user input and execute the application logic.

### `application.py`

The `MyApp` class is a subclass of `quickfix.Application` and defines methods to handle various events during a session. These include session creation, logon, logout, administrative messages, and application-level messages handling. The class also contains methods for sending new orders, cancelling orders, and receiving messages from the server.

---

## How the Application Works

1. **Session Initialization:**
   - The `onCreate` method is called when a FIX session is created.
   - The `onLogon` method is called upon successful logon to the FIX server.

2. **Message Processing:**
   - The `fromApp` method processes incoming application-level messages.
   - The `process_incoming_message` method parses and handles specific message types such as execution reports and order cancel rejects.

3. **Order Handling:**
   - The `new_order` method creates and sends a new order with the selection of ticker symbol, side, and order type being generated at random.
   - The `cancel_order` method creates and sends a request to cancel a randomly selected order.

4. **User Interaction:**
   - The `run` method provides a command-line interface for the user to either send new orders or exit the application.

5. **Session Termination:**
   - The `logout_request` method sends a logout request to gracefully terminate the FIX session.

6. **Execution:**
   - The `schedule` method repetitively sends new orders and introduces a 50% chance of randomly canceling an order. The number of messages to be sent can be changed as desired (currently set at 1000).

7. **Exit:**
   - The user can choose to exit the application, which triggers the `exit_app` method, sending a logout request and terminating the session after key trade statistics (Total Volume, PnL, and VWAP) are calculated and displayed after executint the ```calculate_statistics``` method.

---

The application was developed for educational and POC purposes only. In its current form, all admin- and application-level messages (going to and from the server) are printed in the console (the SOH character in a message has been replaced by the pipe character ("|") for better visibility). This could be useful, for example, in troubleshooting some client-server exchange issues with a specific broker. In addition, the trade statistics were only limited for filled Buy orders only. Future version of the application will be developed to include more functionalities (e.g. for short selling).
