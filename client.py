import quickfix as fix
import sys
import argparse
from application import MyApp

def main(configfile):
    try:
        settings = fix.SessionSettings(configfile)
        application = MyApp()
        storeFactory = fix.FileStoreFactory(settings)
        logFactory = fix.FileLogFactory(settings)
        initiator = fix.SocketInitiator(application, storeFactory, settings, logFactory)
        initiator.start()
        application.run()
        initiator.stop()

    except fix.ConfigError as e:
        print("ConfigError:", e)
        initiator.stop()
        sys.exit()

    except fix.RuntimeError as e:
        print("RuntimeError:", e)
        initiator.stop()
        sys.exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='FIX Client')
    parser.add_argument('-c', '--configfile', default="configfile.cfg", help='file to read the config from')
    args = parser.parse_args()
    main(args.configfile)