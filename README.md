# Telegram bot with Google sheets API #

#### Bot keeps records of funds spent and received with an entry in Google sheets  ####

Warning: No need to write headings in the Google table, the bot will fill them in automatically.

All you need is to create 2 sheets in a Google spreadsheet and add the bot to the telegram chat.

Activate venv:
```
$ source venv/bin/activate
```

Start command to run app:
```
$ nohup python3 main.py &
```

To stop app you need to kill active python3 pid:
```
$ ps -ef
$ kill [pid number] 
```



