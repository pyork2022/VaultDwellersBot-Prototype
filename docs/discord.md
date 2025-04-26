

<img src="docs/images/owlmind-banner.png" width=800>

### [Understand](../README.md) | [Get Started](../README.md#getting-started) | [Contribute](../CONTRIBUTING.md)




# How-to Create a Discord Bot?

This document explains how to create a Discord Bot and collect the TOKEN and URL you will need to connect to the running environment.

You will need:
1. Create a DISCORD TOKEN 
2. Generate the URL to attach the Bot to our Server
3. Connect your Bot to an OwlMind Bot Runner
4. Connect your Bot to an OwlMind 

## 1. Create a DISCORD TOKEN 

#### Go to Discord Developer Portal and login:

[https://discord.com/developers/docs/intro](https://discord.com/developers/docs/intro)


#### Click on 'Applications' (top-left)

#### In the 'Applications' page, click on 'New Application'

![Application->New Application](/docs/images/discord-1.png)


#### Provide a Name and Description

This will show in Discord later, thus e.g enter the name of your Project Group and a Quick Description of your group (name, class code) and project.

> Note:
> Change only Name and Description; DO NOT mess with any other parameters on this page!


####  Click on 'Bots' menu

![Bot Name](/docs/images/discord-2.png)

#### Basic bot configuration:

1. Enable PUBLIC BOT
1. Enable MESSAGE CONTENT INTENT
1. Make sure that Require OAuth2 Code Grant IS NOT checked
1. Add an Icon

* Don't worry about the 'Permissions'
* SAVE IT

> [IMPORTANT}
> Without MESSAGE CONTENT INTENT enabled your Bot will not start!
> It will return an error message like:
>
> raise PrivilegedIntentsRequired(exc.shard_id) from None
> discord.errors.PrivilegedIntentsRequired: Shard ID None is requesting privileged intents that have not been explicitly enabled __

![Bot Configuration](/docs/images/discord-3.png)

(1.i) click RESET TOKEN

![Generate TOKEN](/docs/images/discord-6.png)


> NOTE:
> The TOKEN will only show up AFTER you click 'RESET TOKEN'


## 2. Generate the URL to attach the Bot to our Server

Got 'OAuth2':

1. Select 'Bot' from 'OAuth2 URL Generator'
1. Select all entries under 'Text Permissions' (within 'Bot Permissions')
1. Copy the URL from 'Generated URL'

![Bot Configuration](/docs/images/discord-4.png)

![Bot OAuth](/docs/images/discord-7.png)


## 3. Deploy the Bot to our Discord Server

* You must be ADMIN (or have "Manage Server") permission to invite the Bot.
* At this point reach out to the the Teacher, TA or designated Master of Bots:
  * Provide the URL from 'Generated URL' from Step (2)
* After the Bot has been invited into the Server, you should be able to check its presence by typing in the handler e.g. @DemoBot.
* The Bot will be inactive until you complete step (4) and connect this Bot Application to a OwlMind Bot Runner (and execute it).

![Bot Permissions](/docs/images/discord-8.png)


## 4. Connect your Bot to an OwlMind 

Continue the steps in [INSTALLING.me](../INSTALLING.md#2-configure-your-discord-bot)






