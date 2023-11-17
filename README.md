# FIX Client Application

This FIX (Financial Information eXchange) client application serves as an example of a basic trading system that communicates with a FIX server. The application is written in Python and uses the QuickFIX library to handle FIX protocol messaging. The client can send new orders, cancel existing orders, and receive execution reports.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Application Design](#application-design)
- [How the Application Works](#how-the-application-works)

---

## Installation

To run the FIX client application, you need to have Python installed on your system. Additionally, install the required dependencies using the following command:

```bash
pip install quickfix
```

---

## Configuration

The configuration for the FIX client is specified in the `configfile.cfg` file. This file contains settings for the FIX session, such as connection details, session parameters, and file paths for logging and storing messages.

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

Adjust the configuration settings according to your FIX server specifications.

---

## Usage

To run the FIX client application, execute the `client.py` script from the command line. You can provide a custom configuration file using the `-c` option:

```bash
python client.py -c your_configfile.cfg
```

Follow the prompts to interact with the application, either to send new orders or to exit the application.

---

## Application Design

The application consists of two main components: `client.py` and `application.py`. The `client.py` script initializes the FIX session and starts the application, while the `application.py` script defines the behavior of the FIX application.

### `client.py`

This script sets up the FIX session using the provided configuration file. It creates an instance of the `MyApp` class, which is defined in `application.py`. The FIX session is initiated using the QuickFIX library, and the application's main loop is run to handle user input and execute the application logic.

### `application.py`

The `MyApp` class is a subclass of `fix.Application` and defines callback methods to handle various events in the FIX protocol lifecycle. These events include session creation, logon, logout, administrative messages, and application-level messages. The class also contains methods for sending new orders, cancelling orders, and scheduling order-related actions.

---

## How the Application Works

1. **Session Initialization:**
   - The `onCreate` method is called when a FIX session is created.
   - The `onLogon` method is called upon successful logon to the FIX server.

2. **Message Processing:**
   - The `fromApp` method processes incoming application-level messages.
   - The `process_incoming_message` method parses and handles specific message types such as execution reports and order cancel rejects.

3. **Order Handling:**
   - The `new_order` method creates and sends a new order.
   - The `cancel_order` method creates and sends a request to cancel a randomly selected order.

4. **User Interaction:**
   - The `run` method provides a command-line interface for the user to either send new orders or exit the application.

5. **Session Termination:**
   - The `logout_request` method sends a logout request to gracefully terminate the FIX session.

6. **Execution:**
   - The `schedule` method repetitively sends new orders and introduces a 50% chance of randomly canceling an order.

7. **Exit:**
   - The user can choose to exit the application, which triggers the `exit_app` method, sending a logout request and terminating the session.

---

Feel free to customize the application to suit your specific use case or integrate it into a larger trading system. For more information on the FIX protocol and QuickFIX, refer to the respective documentation.

*Note: This documentation assumes basic familiarity with FIX protocol concepts and Python programming.*
