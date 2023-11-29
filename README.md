# discord-threads-suck
Discord threads auto-hide after a week if you don't post anything. They should not do that.

This bot begrudgingly works around this problem in a very primitive way - it simply posts a message in the thread at a specified interval to keep it 'active'.

Commands:
* `!keepalive` - enable bot updates in the current channel.
* `!interval <minutes>` - set the interval to a specified amount of minutes
* `!debug` - print registered targets and active tasks

Create a file named `token.txt` in the working directory of the script containing your bot token.
It will need permission to read your messages. (I think there's an alternate way of doing this with the commands API, but meh.)

The script will generate its own `targets.json` to keep track of active targets between reboots.