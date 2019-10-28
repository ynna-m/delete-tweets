# Delete tweets

![](https://github.com/koenrh/delete-tweets/workflows/build/badge.svg)

This is a simple script that helps you delete tweets (or just replies or retweets)
from your timeline. There are quite a few third-party services that allow you
to delete tweets, but these very likely will not allow you to delete tweets beyond
the infamous [3,200 tweet limit](https://web.archive.org/web/20131019125213/https://dev.twitter.com/discussions/276).

## Prerequisites

Unfortunately, as of late 2018, you are required to have a Twitter Developer account
in order to create a Twitter app.

### Apply for a Twitter Developer account

1. [Create a Twitter Developer account](https://developer.twitter.com/en/apply):
    1. **User profile**: Use your current Twitter @username.
    1. **Account details**: Select *I am requesting access for my own personal use*,
      set your 'Account name' to your @username, and select your 'Primary country
      of operation.
    1. **Use case details**: select 'Other', and explain in at least 300 words that
      you want to create an app to semi-automatically clean up your own tweets.
    1. **Terms of service**: Read and accept the terms.
    1. **Email verification**: Confirm your email address.
1. Now wait for your Twitter Developer account to be reviewed and approved.

### Create a Twitter app

1. [Create a new Twitter app](https://developer.twitter.com/en/apps/create) (not
  available as long as your Twitter Developer account is pending review).
1. Set 'Access permissions' of your app to *Read and write*.

### Configure your environment

1. Open your Twitter Developer's [apps](https://developer.twitter.com/en/apps).
1. Click the 'Details' button next to your newly created app.
1. Click the 'Keys and tokens' tab, and find your keys, secret keys and access tokens.
1. Now you need to make these keys and tokens available to your shell environment.
  Assuming you are using [Bash](https://en.wikipedia.org/wiki/Bash_(Unix_shell)):

:warning: Before you continue, you should be aware that most shells record user
input (and thus secrets) into a history file. In Bash you could prevent this by
prepending your command with a _single space_ (requires `$HISTCONTROL` to be set
to `ignorespace` or `ignoreboth`).

```bash
export TWITTER_CONSUMER_KEY="your_consumer_key"
export TWITTER_CONSUMER_SECRET="your_consumer_secret"
export TWITTER_ACCESS_TOKEN="your_access_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret"
```

### Get your tweet archive

1. Open the [Your Twitter data page](https://twitter.com/settings/your_twitter_data).
1. Scroll to the 'Download your Twitter data' section at the bottom of the page.
1. Re-enter your password.
1. Click 'Request data', and wait for the email to arrive.
1. Follow the link in the email to download your Tweet data.
1. Unpack the archive, and move `tweet.js` to the same directory as this script.

## Getting started

### Local

First, install the required dependencies.

```bash
pip install -r requirements.txt
```

Then, for example, delete any tweet from _before_ January 1, 2018:

```bash
python deletetweets.py -d 2018-01-01 tweet.js
```

Or only delete all retweets:

```bash
python deletetweets.py -r retweet tweet.js
```

### Spare tweets

You can optionally spare tweets by passing their `id_str`, setting a minimum amount of likes or retweets:

```bash
python deletetweets.py -d 2018-01-01 tweet.js --spare-ids 21235434 23498723 23498723
```

Spare tweets that have at least 10 likes, or 5 retweets:

```bash
python deletetweets.py -d 2018-01-01 tweet.js --spare-min-likes 10 --spare-min-retweets 5
```

### Docker

Alternatively, you could run this script in a [Docker](https://docs.docker.com/install/)
container.

First, you need to build the Docker image.

```bash
docker build -t koenrh/delete-tweets .
```

Then, run the script using the following command.

:warning: Before you continue, you should be aware that most shells record user
input (and thus secrets) into a history file. In Bash you could prevent this by
prepending your command with a _single space_ (requires `$HISTCONTROL` to be set
to `ignorespace` or `ignoreboth`).

```bash
docker run --env TWITTER_CONSUMER_KEY="$TWITTER_CONSUMER_KEY" \
  --env TWITTER_CONSUMER_SECRET="$TWITTER_CONSUMER_SECRET" \
  --env TWITTER_ACCESS_TOKEN="$TWITTER_ACCESS_TOKEN" \
  --env TWITTER_ACCESS_TOKEN_SECRET="$TWITTER_ACCESS_TOKEN_SECRET" \
  --volume "$PWD:/app" --rm -it koenrh/delete-tweets -d 2018-01-01 /app/tweet.js
```

You could make this command more easily accessible by putting it an executable,
and make sure that it is available in your `$PATH`.

##UPDATES - PLEASE READ##
:warning: WARNING: BEFORE USING THE FOLLOWING ADDITIONAL OPTIONS IN THIS FORK, PLEASE BE
WARNED THAT I CAN'T GUARANTEE COMPLETELY IF THESE OPTIONS WILL WORK ON YOUR END.
SO USE THIS FORK WITH CAUTION. THEY SAY MASS DELETING YOUR TWEETS CAN CAUSE BUGS
IN YOUR TIMELINE, SO AGAIN, USE THIS WITH CAUTION.
-by Ynna M.G.

###Additional Options
1. ```-om ```  = Spare your own media tweets from deletion. It also works if you use -r
to restrict deletion of your tweets to "reply". It will save your replies with
any media in it.
1. ```-rtm``` = Spare retweets containing media from deletion. Sometimes works,
sometimes doesn't. It depends on how your retweet was recorded by Twitter. Don't
know the exact way they record, but there are retweets that don't contain the "media"
key under the "entities" key, but the retweet itself, when you check on Twitter,
does have a picture, video, animated_gif, etc. in it. And yet there are also retweets
that do contain the "media" key. ```-rtm``` is based on checking whether the retweet
has a "media" key on it. So it works on some cases that has it.
1. ```--spare-list```  = By default, uses to_save.txt file in the same directory as
the script. This was added in case any of you guys have saved a lot of tweets
saved and --spare-ids isn't cutting it anymore. You can change the path to your
own txt file using this option
1. ```--keyword``` = is based on @sepi2048's fork, with minor modifications. Modified
it to be able to search multiple keywords and phrases. Basically made keyword as a list
instead. So to be able to spare tweets containing a phrase, put the phrase in
"quotation marks". Any additional keywords or phrases can be separated by a white space
like in --spare-ids
