Traceback (most recent call last):
  File "tweepy_streamer.py", line 1, in <module>
    from tweepy.streaming import StreamListener
  File "/gpfsnyu/scratch/akb523/Scripts/venv-urban/lib/python3.7/site-packages/tweepy/__init__.py", line 18, in <module>
    from tweepy.streaming import Stream, StreamListener
  File "/gpfsnyu/scratch/akb523/Scripts/venv-urban/lib/python3.7/site-packages/tweepy/streaming.py", line 13, in <module>
    import ssl
  File "/gpfsnyu/packages/python/gnu/3.7.3/lib/python3.7/ssl.py", line 98, in <module>
    import _ssl             # if we can't import it, let the error propagate
ImportError: /lib64/libcrypto.so.10: version `OPENSSL_1.0.2' not found (required by /gpfsnyu/packages/python/gnu/3.7.3/lib/python3.7/lib-dynload/_ssl.cpython-37m-x86_64-linux-gnu.so)
