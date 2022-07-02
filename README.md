# Skye
 <b>An all in one open source Multi-Purpose Discord Bot! </b>
  
  
# Self-hosting
We provide a few ways to self-host Skye. <br>
A main way is using PM2 which is sufficent but requires you to have postgres pre-installed on your machine pre-made and all, though PM2 is the fastest and probably the easiest way to self-host, our next choice might be the best. <br>

How to self-host with PM2

- Install PM2 from [the PM2 website](https://pm2.keymetrics.io/)
- CD into the bot directory and then run ``pm2 start pm2.json`` which will open the bot with pm2. <br>
(Note, If you are using this method, make sure you have lavalink installed and you have postgres 13 or up installed on your system and setup) <br>
the way to open the logs for the bot running with PM2 is by using the command ``pm2 log insertthepm2botprocessnameorid``

<br>
Another way to selfhost skye is too use docker. we provide a dockerfile and docker-compose files pre made (they may not work because the postgres image thingys are dumb) <br>
How to self-host with docker is as of follows <br>

- Install docker on your machine as you would normally
- After you do that, cd into the bot directory and run `` docker-compose up -d --build`` in your terminal to build all the bot processes including lavalink and the postgres image.
- Once you do that, make sure to run this command in discord <br> ``yourbotprefix jsk py await bot.pool.execute(STARTUP_QUERY)`` (replace yourbotprefix with the bot prefix you chose) which will make all table and relations in your database.
- Enjoy skye running on docker!

if there are any issues with self-hosting with either of these, please open an issue or if you want to fix something in say the docker files, please fork this repo and open a pull request. 

