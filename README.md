# Slotlist

Slotlist is a discord bot, that can manage preplanned missions. It is mostly written for Arma 3 missions, but can be used for games like DCS.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You need Python 3 to run the bot. You can have multiple Python versions (2.x and 3.x) installed on the same system without problems.
In Ubuntu, Mint and Debian you can install Python 3 like this:

```
$ sudo apt-get install python3 python3-pip
```

For other Linux flavors, macOS and Windows, packages are available at

[http://www.python.org/getit/](http://www.python.org/getit/)

Also you need to have sqlite3 but it is in the standard library from python3.
Check the preinstalled version with:
```
sqlite3 -version
```
If there is not a version number, you need to check either your python3 installation or install sqlite3.

### Installing

First you need to install the discord library for python.

```
$ python3 -m pip install -U discord.py
```
and one windows the following would be used.
```
> py -3 -m pip install -U discord.py
```
Also you need to have pyperclip installed
```
$ pip install pyperclip
```

Now you need to set-up your database.
We will create a database with:
```
$ sqlite3 slotlist.db
```
And we need to create one table for the missions list:
```
sqlite3> CREATE TABLE missions (mission_id INTEGER PRIMARY KEY, mission_name TEXT NOT NULL);
```
Now exit the database environment:
```
sqlite3> .quit
```

You can use the [init-database.py](init-database.py) script for doing that job for you.
```
$ python3 init-database.py
```

<!--
## Deployment

Add additional notes about how to deploy this on a live system
-->
## Built With

* [discord.py](https://discordpy.readthedocs.io/en/latest/) - The bot env for discord
* [SQLite3](https://www.sqlite.org/index.html) - Database managing

## Contributing

Please read [CONTRIBUTING](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/Katalam/slotlist-discord-bot/tags).

## Authors

* [Katalam](https://github.com/Katalam) - *Initial work*

<!-- See also the list of [contributors](https://github.com/Katalam/slotlist-discord-bot/contributors) who participated in this project. -->

## License

This project is licensed under the GPLv3 - see the [LICENSE](LICENSE) file for details
