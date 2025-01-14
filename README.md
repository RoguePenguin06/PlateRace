# 🏎️ PlateRace - A computer vision racing game where anything, including a paper plate, can be your steering wheel!

A game to learn `pygame` and computer vision controls built as part of the AWS Game Builder Challenge. Checkout our submission [here](https://devpost.com/software/wip-jg3vpe).

## Requirements
Clone the repository:`git clone https://github.com/MgnMtn/PlateRace`

**Install dependencies:**

Apple Silicon:
 - Install Python 3.11.
 - Run `pip3.11 install -r requirements.txt`

Other systems:
 - Ensure Python 3 is installed.
 - Run `pip3 install -r requirements.txt`

**Run the game:**

Apple Silicon:
 - Execute `python3.11 PlateRace`

Other systems:
 - Execute `python3 PlateRace`

## Inspiration
Originally meant to be a paper plate as the controller, hence the name PlateRace. Since we used hand tracking instead, you can hold anything or even nothing, and it still works just as well.

## What it does
A two player game that uses your camera to track your hands which lets you steer the car in game.

## How we built it
Split the game and controller between us and integrated them with Q Developer
The game was made with Pygame as a way of learning the library for school work.
The hand-tracking controller used Google's media pipe library to track the hands, and then we used it to control the cars. We used an S3 bucket to store the assets; however, we only worked out how to do this for an individual user, so we have not merged this branch into the main.

## Challenges we ran into
At first, the game ran very slowly due to the camera making it almost unplayable so we had to reduce how many times it processed the image every second

## Accomplishments that we're proud of
Allowing the camera to distinguish between two players at once
Managing to combine our parts in a way that worked how we envisioned it

## What we learned
How to use Github
Use of object oriented programming and small shortcuts to use in any project
Using mediapipe and setting up AWS services (still a lot to learn)

## What's next for PlateRace
More levels, speed boosts, single player mode
Adding more players onto one camera or even online games
