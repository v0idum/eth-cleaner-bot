START_SUBJECT = '{} ETH Cleaner Started!'
START_BODY = '{}\n\nScript ver. {} started!'

DAILY_REPORT_SUB = '{} ETH Cleaner Daily Report'
DAILY_REPORT_BODY = '''{}

Status: Running
Start : {}
Uptime: {} days, {} hours, {} minutes
Script ver. {}

ETH balance: {} (${})

Control1: {}
Control2: {}
'''

NEW_DEPOSIT_SUB = '{} ETH Available!'
NEW_DEPOSIT_BODY = '''{}

Balance updated, there is ETH to send
Current balance: {} ETH
'''

TX_SUCCESS_SUB = '{} ETH Transfer Success!'
TX_SUCCESS_BODY = '''{}

{} ETH transferred from {}
to {}

Tx hash: {}
Tx Fee: {} ETH (${})
'''

TX_FAIL_SUB = '{} Error! ETH Transfer Failed!'
TX_FAIL_BODY = '''{}

Tx hash {}
Tx: {}
Receipt: {}
'''
