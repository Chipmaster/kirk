kirk is a python application which allows one to quickly and easily rename a collection of tv files with a preferred structure.  kirk uses configurable regular expressions to extract the metadata necessary to query a unique episode from a tv database.  A simple markup language is defined, similar to picard which allows a user to customize the format of the renamed file.


# Example Session #
```
>>$ ls -R Pioneer\ One/
Pioneer One/:
Season 1

Pioneer One/Season 1:
pioneer.one.s01e01.avi  pioneer.one.s01e03.avi  pioneer.one.s01e05.avi
pioneer.one.s01e02.avi  pioneer.one.s01e04.avi  pioneer.one.s01e06.avi
>>$ kirk Pioneer\ One
>>$ ls -R Pioneer\ One/
Pioneer One/:
Season 1

Pioneer One/Season 1:
Pioneer One - S01E01 - Earthfall (Pilot).avi   Pioneer One - S01E04 - Triangular Diplomacy.avi
Pioneer One - S01E02 - The Man From Mars.avi   Pioneer One - S01E05 - Sea Change.avi
Pioneer One - S01E03 - Alone in the Night.avi  Pioneer One - S01E06 - War of the World.avi
```


# Downloads #
Use "Featured Downloads" on the left hand side. For more options and information, go to the Downloads tab.

git repo: https://code.google.com/p/kirk/

# Features #
  * User defined perl style regular expressions to parse various file names.
```
.*\.[sS]([0-9]{2,2})[eE][0-9]{2,2}\..*
```
  * Customizable output format with markup language.
```
%Name% - S%season%E%episode% - %Title%
```
  * Backup option to create hard links with the existing file names for easy reversion

# Some Ideas for Future Development #
  * GUI to stage renames and make regular expression formatting easier. Modeled after picard.
  * Investigate modifying video tags
  * Full plugin system so that you can scrape info from more than TV Rage
  * Develop automated testing suite
  * List of accepted extensions to operate on
  * Depreciate showid option. When there are multiple results for a parsed name, show them to the user and let the user decide.  When no name can be found, let a user enter one.