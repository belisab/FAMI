# :musical_note: Epic (and also awesome) :sparkles:Musical Searching Application:sparkles:

Courtesy of FAMI Co. (Fiia, Aaro, Manuel, Isabel)

## :rocket: What does this app do?

With this app, you can search through a database of musicals. Ever wanted to know every musical that features dogs? Trying to find more musicals about deranged high schoolers to fill a Heathers-shaped hole in your heart? Then this app is for you!

There are three search methods: boolean, TF-IDF, and semantic. Boolean search just checks if the words you search for match our any of the musicals in our database. TF-IDF is a little more sophisticated and also checks if the words you use are themselves common; for example, nearly everything contains the word "musical", so it's not very informative. Semantic search uses the `glove-wiki-gigaword-300` to parse your query and find results that try to more accurately match the meaning of your search.

## :nail_care: How to run the app

### :mage: If you've run Flask apps before:

The app lives in `search_engine_project`. Install dependencies and run the Flask app. No out-of-the-ordinary extra setup to be found here.

### :snake: If you've used Python before:

0. (Set up venv by running `python3 -m venv .venv`, then on Windows run `./venv/Scripts/activate.bat` or on other platforms `source .venv/bin/activate`)
1. Run `pip3 install -r requirements.txt`
2. Run `cd search_engine_project`
3. RUn `python3 -m flask run`

### :baby: For everyone else:

> You're going to need to clone this repository locally and navigate to the directory in the terminal. If you don't know how to do that, you should take the course Command Line Tools for Linguists. Or run `git clone https://github.com/belisab/FAMI; cd FAMI`.

To run the app, **you need to have at least Python 3.10 installed**. You can check your Python version by running `python3 -V` in the terminal. If it's 3.10 or newer, you're set to go!

First, **install dependencies via PIP**. All dependencies are listed in `requirements.txt`, so you can install them by just running `pip3 install -r requirements.txt`. Some of the dependencies might not work on Windows; if you run into issues with that, probably just open up the app on a different computer or VM running Linux instead, because solving Windows issues is one of the worst pasttimes you could have :(

After you have the dependencies installed, navigate to the project directory with `cd search_engine_project`. You can then start the app up with `python3 -m flask run`. This should start up the app on your local computer; you can open it by going to http://localhost:5000/search.

## :people_holding_hands: How the app was made

We worked together and did a lot of pair coding, so the commits don't correctly represent everyone's efforts.

## :computer: Instructions for developing the app:

1. Every time you start working on the project, start off by **pulling the changes** from the cloud repository. You can do this by using your code editor's Git controls (there should be a button labeled "Pull" somewhere, possibly under a "VCS" or "Commits" tab), or manually by running `git pull` in the terminal.

> [!WARNING]
> If there are merge conflicts, oh dear. Send a message to the WhatsApp group or the course Slack team, someone'll help :D

2. After you have made your changes, you need to **commit your work** by running `git commit -a -m "Your message here..."` or by pressing your code editor's "Commit" button. If you have added new files, you need to first run `git add .` (or select the files in your code editor)

3. Once you are finished, run `git push` or press a Push button in your code editor.

> [!WARNING]
> If the push fails (if you get yellow text in the terminal or your code editor complains), then you need to first pull changes (and probably resolve a merge conflict).

If you run into any issues, send a message to the WhatsApp group :D

### :hammer: How to use Venv

Venv (Virtual Environment) is a way to make dealing with Python packages a little less terrible. It should make it so that everyone has the same package versions installed, and we get less "it works on my machine" errors.

Using venv works like this: 

1. On your first time, run `python3 -m venv .venv` to initialize it
2. On Windows, run `./.venv/Scripts/activate`; on MacOS or Linux, run `source .venv/bin/activate`
3. Install packages with `pip3 install -r requirements.txt`
4. You're good to go! If you install any new packages, add them to `requirements.txt`
