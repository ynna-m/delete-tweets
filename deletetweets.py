#!/usr/bin/env python

import argparse
import io
import os
import sys
import time
import json
import re

import twitter
from dateutil.parser import parse

__author__ = "Koen Rouwhorst"
__version__ = "1.0.0"


class TweetDestroyer(object):
    def __init__(self, twitter_api):
        self.twitter_api = twitter_api

    def destroy(self, tweet_id):
        try:
            print("delete tweet %s" % tweet_id)
            self.twitter_api.DestroyStatus(tweet_id)
            # NOTE: A poor man's solution to honor Twitter's rate limits.
            time.sleep(0.5)
        except twitter.TwitterError as err:
            print("Exception: %s\n" % err.message)


class TweetReader(object):
    def __init__(self, reader, date=None, restrict=None, spare=[], min_likes=0, min_retweets=0,
                 spare_list=None, own_media=False, rt_media=False, keyword=[]):
        self.reader = reader
        if date is not None:
            self.date = parse(date, ignoretz=True).date()
        self.restrict = restrict
        self.spare = spare
        self.min_likes = 0 if min_likes is None else min_likes
        self.min_retweets = 0 if min_retweets is None else min_retweets
        if spare_list is None:
            self.spare_list = "to_save.txt"
        else:
            self.spare_list = spare_list
        self.own_media = False if own_media is None else own_media
        self.rt_media = False if rt_media is None else rt_media
        self.keyword = keyword

    def read(self):
        sparedcount = 0
        for row in self.reader:
            if row.get("created_at", "") != "":
                tweet_date = parse(row["created_at"], ignoretz=True).date()
                if self.date != "" and \
                        self.date is not None and \
                        tweet_date >= self.date:
                    continue

            if (self.restrict == "retweet" and
                    not row.get("full_text").startswith("RT @")) or \
                    (self.restrict == "reply" and
                     row.get("in_reply_to_user_id_str") is None):
                sparedcount = sparedcount + 1
                continue

            if row.get("id_str") in self.spare:
                sparedcount = sparedcount + 1
                continue

            if (self.min_likes > 0 and int(row.get("favorite_count")) >= self.min_likes) or \
                    (self.min_retweets > 0 and int(row.get("retweet_count")) >= self.min_retweets):
                sparedcount = sparedcount + 1
                continue

            skip = False
            with open(self.spare_list,"r") as spare_idlist:
                for line in spare_idlist:
                    if row.get("id_str") in line:
                        skip = True
                        break
            if skip is True:
                sparedcount = sparedcount + 1
                continue

            if (self.own_media and row.get("entities").get("media")) and \
                    (not row.get("full_text").startswith("RT @") or \
                     row.get("in_reply_to_user_id_str") is not None):
                sparedcount = sparedcount + 1
                continue

            if (self.rt_media and row.get("entities").get("media")) and \
                    row.get("full_text").startswith("RT @"):
                sparedcount = sparedcount + 1
                continue

            if self.keyword:
                skip = False
                tweet_text = str(row.get("full_text").encode("utf-8"))
                for kw in self.keyword:
                    if re.search(r"\b{}\b".format(kw), tweet_text, re.IGNORECASE) is not None:
                        skip = True
                        break
                if skip is True:
                    sparedcount = sparedcount + 1
                    continue
            yield row
        print("Number of Tweets spared from deletion %s:" % sparedcount)


def delete(tweetjs_path, date, r, s, min_l, min_r, spare_l, o_m, rt_m, k):
    with io.open(tweetjs_path, mode="r", encoding="utf-8") as tweetjs_file:
        count = 0

        api = twitter.Api(consumer_key=os.environ["TWITTER_CONSUMER_KEY"],
                          consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
                          access_token_key=os.environ["TWITTER_ACCESS_TOKEN"],
                          access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"])
        destroyer = TweetDestroyer(api)

        tweets = json.loads(tweetjs_file.read()[25:])
        for row in TweetReader(tweets, date, r, s, min_l, min_r,
                               spare_l, o_m, rt_m, k).read():
            destroyer.destroy(row["id_str"])
            count += 1

        print("Number of deleted tweets: %s\n" % count)


def main():
    parser = argparse.ArgumentParser(description="Delete old tweets.")
    parser.add_argument("-d", dest="date", required=True,
                        help="Delete tweets until this date")
    parser.add_argument("-r", dest="restrict", choices=["reply", "retweet"],
                        help="Restrict to either replies or retweets")
    parser.add_argument("file", help="Path to the tweet.js file",
                        type=str)
    parser.add_argument("--spare-ids", dest="spare_ids", help="A list of tweet ids to spare",
                        type=str, nargs="+", default=[])
    parser.add_argument("--spare-min-likes", dest="min_likes",
                        help="Spare tweets with more than the provided likes", type=int, default=0)
    parser.add_argument("--spare-min-retweets", dest="min_retweets",
                        help="Spare tweets with more than the provided retweets", type=int, default=0)
    parser.add_argument("--spare-list", dest="spare_list",
                        help="Set path for txt file of tweet IDs list to spare")
    parser.add_argument("-om", dest="own_media", nargs='?', const=True, default=False,
                        help="Spare your own media files from deletion")
    parser.add_argument("-rtm", dest="rt_media", nargs='?', const=True, default=False,
                        help="Spare your retweets with media files from deletion")
    parser.add_argument("--keyword", dest="keyword", nargs='+', default=[],
                        help="Keyword in tweets to delete")

    args = parser.parse_args()

    if not ("TWITTER_CONSUMER_KEY" in os.environ and
            "TWITTER_CONSUMER_SECRET" in os.environ and
            "TWITTER_ACCESS_TOKEN" in os.environ and
            "TWITTER_ACCESS_TOKEN_SECRET" in os.environ):
        sys.stderr.write("Twitter API credentials not set.")
        exit(1)

    delete(args.file, args.date, args.restrict, args.spare_ids, args.min_likes, args.min_retweets,
           args.spare_list, args.own_media, args.rt_media, args.keyword)


if __name__ == "__main__":
    main()
