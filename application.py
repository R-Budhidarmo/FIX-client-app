import quickfix as fix
import sys
import random
import time
from datetime import datetime
import pandas as pd

__SOH__ = chr(1)

class MyApp(fix.Application):

    def __init__(self):
        super().__init__()
        self.execID = 0
        self.order_data = []
        self.execution_reports = []

    def onCreate(self, sessionID):
        self.sessionID = sessionID
        print("\n========================================================================================")
        print("\nSession created - Session ID: ", sessionID)
        pass

    def onLogon(self, sessionID):
        self.connected = True
        print("\nLogon successful for session: ", sessionID)
        print("\n========================================================================================")
        pass

    def onLogout(self, sessionID):
        self.connected = False
        print("\n========================================================================================")
        print("\nLogout successful for session: ", sessionID)
        pass
    
    def toAdmin(self, message, sessionID):
        msg = message.toString().replace(__SOH__, "|")  # replace SOH with "|" for better readibility
        print("\nMessage - toAdmin:\n" + msg)
        pass
    
    def fromAdmin(self, message, sessionID):
        msg = message.toString().replace(__SOH__, "|")
        print("\nMessage - fromAdmin:\n" + msg)
        pass
    
    def toApp(self, message, sessionID):
        msg = message.toString().replace(__SOH__, "|")
        print(msg)
        pass
    
    def fromApp(self, message, sessionID):
        self.process_incoming_message(message)
        pass

    def process_incoming_message(self, message):

        # process incoming messages from server
        msgType = fix.MsgType()
        message.getHeader().getField(msgType)

        if msgType.getValue() == fix.MsgType_Reject:
            print("\nReject:\n", message.toString().replace(__SOH__, "|"))
            pass

        elif msgType.getValue() == fix.MsgType_ExecutionReport:
            print("\nExecution Report:\n", message.toString().replace(__SOH__, "|"))

            exec_type = fix.ExecType()
            message.getField(exec_type)     # get values for ExecType (tag 150)

            execution_report = {}
            # Check if the execution report is a fill or partial fill
            # If True, extract relevant data & store in execution_reports dict
            if exec_type.getValue() in ['1', '2']:
                execution_report['ClOrdID'] = message.getField(fix.ClOrdID()).getString()       # tag 11
                execution_report['ExecID'] = message.getField(fix.ExecID()).getString()         # tag 17
                execution_report['Symbol'] = message.getField(fix.Symbol()).getString()         # tag 55
                execution_report['Side'] = message.getField(fix.Side()).getString()             # tag 54
                execution_report['LastShares'] = message.getField(fix.LastShares()).getString() # tag 32
                execution_report['LastPx'] = message.getField(fix.LastPx()).getString()         # tag 31
                self.execution_reports.append(execution_report)     # append dict in execution_reports list
 
        elif msgType.getValue() == fix.MsgType_OrderCancelReject:
            print("\nOrder Cancel Reject:\n", message.toString().replace(__SOH__, "|"))
            pass

    def new_order(self):

        # Create a NewOrderSingle message
        message = fix.Message()
        header = message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_NewOrderSingle))    # tag 35

        orderID = str(self.execID).zfill(5)
        # self.order_ids.append(orderID)  # Add the order ID to the list (to be referenced for cancelation)
        message.setField(fix.ClOrdID(orderID))          # tag 11
        self.execID += 1

        print(f"\nSending Order {orderID}")

        # self.order_side.append(fix.Side_BUY)
        message.setField(fix.Side(fix.Side_BUY))        # tag 54

        tckr = random.choice(["MSFT", "AAPL", "BAC"])
        # self.order_symbol.append(tckr)
        message.setField(fix.Symbol(tckr))              # tag 55

        message.setField(fix.OrderQty(random.randint(100, 500)))    # tag 38

        message.setField(fix.OrdType(fix.OrdType_LIMIT))            # tag 40
        message.setField(fix.Price(random.uniform(100, 200)))       # tag 44

        message.setField(fix.HandlInst(fix.HandlInst_MANUAL_ORDER_BEST_EXECUTION))  # tag 21
        message.setField(fix.TimeInForce('0'))                      # tag 59
        message.setField(fix.Text("New Order Single"))              # tag 58

        trstime = fix.TransactTime()
        trstime.setString(datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3])
        message.setField(trstime)                           # tag 60

        fix.Session.sendToTarget(message, self.sessionID)   # send message to server

        # initiate a dict to contain relevant order data
        order_dict = {}
        order_dict['ClOrdID'] = message.getField(fix.ClOrdID()).getString()     # tag 11
        order_dict['Side'] = message.getField(fix.Side()).getString()           # tag 54
        order_dict['Symbol'] = message.getField(fix.Symbol()).getString()       # tag 55
        order_dict['OrderQty'] = message.getField(fix.OrderQty()).getString()   # tag 38
        order_dict['OrdType'] = message.getField(fix.OrdType()).getString()     # tag 40
        order_dict['Price'] = message.getField(fix.Price()).getString()         # tag 44
        
        self.order_data.append(order_dict)     # append dict in order_data list
 
    def cancel_order(self):

        # Choose a random order to cancel by ClOrdID (tag 11)
        order_to_cancel = str(random.choice(range(self.execID))).zfill(5)
        indx = 0
        for i in range(len(self.order_data)):
            if self.order_data[i]['ClOrdID'] == order_to_cancel:
                indx = i    # Get index of the randomly chosen ClOrdID from order_data dict
        
        print(f"\nCancelling Order {order_to_cancel}")

        # create an Order Cancel Request message
        cancel_request = fix.Message()
        header = cancel_request.getHeader()
        header.setField(fix.MsgType(fix.MsgType_OrderCancelRequest))    # tag 35

        orderID = str(self.execID).zfill(5)
        cancel_request.setField(fix.ClOrdID(orderID))                   #  ClOrdID for the cancel request (tag 11)
        self.execID += 1

        cancel_request.setField(fix.OrigClOrdID(order_to_cancel))       # ID of the original order to cancel (tag 41)
        cancel_request.setField(fix.Symbol(self.order_data[indx]['Symbol']))    # Symbol of the order to cancel (tag 55)
        cancel_request.setField(fix.Side(self.order_data[indx]['Side']))        # tag 54
        cancel_request.setField(fix.Text("Order Cancel Request"))       # tag 58

        trstime = fix.TransactTime()
        trstime.setString(datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3])
        cancel_request.setField(trstime)                                # tag 60

        fix.Session.sendToTarget(cancel_request, self.sessionID)    # send message to server

    def logout_request(self):

        # create a Logout Request message
        logout_request = fix.Message()
        header = logout_request.getHeader()
        header.setField(fix.MsgType(fix.MsgType_Logout))            # tag 35
        logout_request.setField(fix.Text("Logout Request"))         # tag 58
        fix.Session.sendToTarget(logout_request, self.sessionID)    # send message to server

    def calculate_statistics(self):

        order_df = pd.DataFrame(self.order_data)
        order_df.to_csv('order_data.csv') # save to csv just to check

        order_df['Price'] = pd.to_numeric(order_df['Price'], errors='coerce')
        order_df['OrderQty'] = pd.to_numeric(order_df['OrderQty'], errors='coerce')
        total_ave_bid = (order_df['Price'] * order_df['OrderQty']).sum() / len(order_df)

        exec_df = pd.DataFrame(self.execution_reports)
        exec_df.to_csv('execution_data.csv') # save to csv just to check

        exec_df['LastShares'] = pd.to_numeric(exec_df['LastShares'], errors='coerce')
        exec_df['LastPx'] = pd.to_numeric(exec_df['LastPx'], errors='coerce')

        # Calculate total trading volume in USD
        exec_df['TotalVolume'] = exec_df['LastShares'] * exec_df['LastPx']
        total_volume_usd = exec_df['TotalVolume'].sum()

        # Calculate PnL (averege bid-ask spread) from trading
        pnl = total_ave_bid - (total_volume_usd / len(exec_df))

        # Calculate VWAP of the fills for each instrument for each ticker symbol
        exec_df1 = exec_df.copy()
        exec_df1 = exec_df1[['ClOrdID','Symbol','LastShares','LastPx']]
        exec_df1['VolTimesPrice'] = exec_df1['LastShares']*exec_df1['LastPx']

        # sort by ClOrdID and group by Symbol
        grouped_data = {name: group.sort_values('ClOrdID') for name, group in exec_df1.groupby('Symbol')}
        
        ticker = ['AAPL','BAC','MSFT']

        # calculate VWAP for each ticker & get last VWAP data
        vwap = []
        for i in ticker:
            grouped_data[i]['VWAP'] = grouped_data[i]['VolTimesPrice'].cumsum()/grouped_data[i]['LastShares'].cumsum()
            vwap.append(round(grouped_data[i]['VWAP'].iloc[-1],2))
        
        # get last price data
        last_price = []
        for i in ticker:
            last_price.append(grouped_data[i]['LastPx'].iloc[-1])

        vwap_df = pd.DataFrame({'Ticker':ticker,'Last Price': last_price, 'Last VWAP':vwap})

        print("\nTRADE STATISTICS")
        print("\nTotal Trading Volume in USD: ", round(total_volume_usd,2))
        print("\nAverage PnL from this session: ", round(pnl,2))

        # print("\nFill Price & VWAP for each ticker: ")
        # for i in ticker:
        #     print(grouped_data[i][['Symbol','LastPx','VWAP']])
        #     print("\n")
        
        print("\nLast Price & VWAP for each ticker: ")
        print(vwap_df)
        print("\n----------------------------------------------------------------------------------------")

    def schedule(self):
        # repeat sending a new order for n number of times
        n = 1000
        for _ in range(n):
            self.new_order()
            # introduce 50% chance of randomly cancel an order
            to_cancel = random.randint(1,2)
            if to_cancel == 1:
                self.cancel_order()

    def exit_app(self):
        self.calculate_statistics()
        time.sleep(2)
        self.logout_request()
        print("\n----------------------------------------------------------------------------------------")
        print("\nExiting the FIX client application. Goodbye!")
        print("\n========================================================================================")
        sys.exit()

    def run(self):
        while True:
            time.sleep(5)
            options = str(input("\nType 1 to put new Orders through, or 2 to Exit, and then hit Enter: "))
            print("\n----------------------------------------------------------------------------------------")

            if options == '1':
                self.schedule()
                time.sleep(5)
                self.run()
            elif options == '2':
                self.exit_app()
            else:
                print("\nValid input is 1 for Orders, 2 for Exit\n")