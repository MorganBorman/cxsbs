from MasterClient import MasterClient
import time

mc = MasterClient("localdomain", "localhost", 28780, 28785, 10)
mc.start()
time.sleep(4)
mc.authentication_request(400, "chasm")
mc.authentication_response(400, raw_input("Enter response: "))