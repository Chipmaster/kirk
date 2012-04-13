#
# Regular cron jobs for the kirk package
#
0 4	* * *	root	[ -x /usr/bin/kirk_maintenance ] && /usr/bin/kirk_maintenance
