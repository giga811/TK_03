# Running server

```sh
$ virtualenv venv # create a virtual environment
$ source venv/bin/activate # activate the venv
(venv)$ CFLAGS='-std=c99' pip install gevent # http://stackoverflow.com/a/32545855/1950204
(venv)$ pip install -r requirements.txt # install requirements inside the venv
(venv)$ python init_db.py # initialize the database
(venv)$ python run.py # run
```

Then open `localhost:5000` on your browser.

## Installing NLP manually

### Installing Mecab
```sh
# on mac
$ brew install mecab
$ brew install mecab-ipadic
$ cd webapp/chat/static
$ pip install mecab-python-0.996.tar.gz
```

[Centos Here](http://qiita.com/saicologic/items/ab70e14f7e2ec2ee0b4d)

### Installing NLTK
```sh
$ python
>>> import nltk
>>> nltk.download()
```