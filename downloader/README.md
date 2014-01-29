Media Content Downloader
========================

This is a collection of scripts to download all the articles from a set of media ids via Media Cloud.  This has been superceeded by recent additions to the MediaCloud API client library, so you probably don't want to start hacking at these scripts for anything.

Install
-------

Follow the instructions to install the [mediacloud api client](https://github.com/c4fcm/MediaCloud-API-Client), then:

```
pip install iso3166 pymongo
```

Scripts
-------

The `download_from_lucene.py` script downloads everything and saves it in a mongo DB.  Then you can run the `generate-json.py` script to create the TF-IDF results (saved to the `output` dir.)