
MediaExchange is a Django based web application. It enables you to share your
media with your peergroup in a secure manner and as low bandwidth for you as
possible. Therefore it uses file hoster to share your media. At the moment only
MultiUpload.com is implemented, but more are to follow. The uploaded files are
encrypted with Blowfish and split into the maximum allowed size allowed by the
file hoster. Afterwards everyone in the peergroup may download the files from
the file hoster and use the decrypter to unpackage it.


SET UP
======

In order to get going you need the following:

```
aptitude install python-django python-crypto python-simplejson
```


If you want to use apache heres a simple snippet:

```
    <Location "/">
        SetHandler python-program
        PythonHandler django.core.handlers.modpython
        SetEnv DJANGO_SETTINGS_MODULE mediaExchange.settings
        PythonDebug On
        PythonPath "['/path/to/Media-Exchange/mediaExchange'] + sys.path"
    </Location>
```


Replace the /path/to/... accordingly.

Notice: Currently it is only possible to run MediaExchange in the webserver root.
        You might want to set up a virtual host.


To fill the database with your media use the meupdatedb.py script and create a
config that suits your needs, e.g.:

```
[DEFAULT]
project = /home/chriz/versioning/Media-Exchange/mediaExchange/
movies = /home/chriz/media/Movies
series = /home/chriz/media/Series,/media/disk42/Series
```

Before running the script you need to set the DJANGO_SETTINGS_MODULE environment
variable:

```
export DJANGO_SETTINGS_MODULE="mediaExchange.settings"
```

The script will parse through the folders and fill the database. There is some
markup to fill the according fields. The movie subfolders should be named after the
following schema:

```
moviename - moviesubtitle (year) [source] |language|/
```

For series the following naming schema is used:

```
seriesname/Season number - seasonsubtitle (year) [source] |language|/
```

e.g.:
```
The Big Bang Theory/Season 2 [DVDRip] |eng|
```

Year, source, language and subtitles are optional.


The medaemon.py script should run at all times. It is responsible to react on
user's wishes. It packages and uploads requested media.

See the /about page for help with decrypting files.
