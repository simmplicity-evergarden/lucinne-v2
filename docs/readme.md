# Lucinne Docs

## User Docs
***SAFEWORD***
To break the effects of the bot, use a reaction with the name `:safeword:` on any recent message. 
***SAFEWORD***

### Filters/Statuses/Afflictions
Lucinne features multiple "statuses" (internally called "afflictions"). These can be applied to server members to have their messages deleted or replaced based on certain conditions. Only one status will be "applied" at a time. The following are each of them in the order they're checked in:

#### Thrall
Activated by: @ing or replying to the server owner with a ping, or added manually  
Effect: All messages are replaced with praise for the server owner.

#### Object
Activated by: manual application only  
Effect: Words are replaced with periods because objects don't speak. In strict mode, the length of the message is fixed to five characters.

#### Feral
Activated by: manual application only  
Effect: Messages are "locked" and replaced with dog sounds. Members can vote to unlock the message or vote to keep it locked. The number of votes required is determined by the command to add this status.  
There is a small chance that the message will be replaced with huffing paws. This can be increased by reacting to the message with the paw emoji.  
Admins can immediately unlock messages by reacting with a key emoji.
Additionally, all images are replaced with pictures of paws.


#### Squeak
Activated by: react to any recent message with `:Rosasmile:`, 🎈, or 💬, or added manually  
Effect: Adds a chance that each word (or message) will be replaced with squeak sounds. Optionally, can also require the member to `**Smile!~` for their message to remain un-squeaked. These can be mixed for a chance at squeaking even if the smile is included.  
The check for **Smile!~** is *very strict*. The message must in include one of the following *exactly*:
- `**Smile!~**`
- `**Smiles!~**`
- `**Smiling!~**`

#### Bot
Activated by: manual application only  
Effect: All messages are deleted and replaced to include the `[Bot]` tag next to the username.   
In strict mode, only a list of pre-made messages can be sent. These messages can be seen by sending "help" while under this effect. The bot will DM you the phrases and keywords. Send the keyword (for example, `418`) and the bot will replace it with the phrase.


### Leashing
A leashed user will be locked down to only the channel they were leashed in. They will be unable to see other channels until freed.

### Name Changing
Members with permission to the `/manage_name` command can rename other members. 

### Member Impersonation
Members with permission to the `/speak_as_member` command can speak as though they were other members. The message will have the `[Bot]` tag as these messages are sent using webhooks.

### Name Locking
Members with permission to the `/manage_role` command can remove others' ability to change their own name. ***This requires the server to be set up to allow such restrictions.***

### Name Locking
Members with permission to the `/manage_role` command can remove others' ability to send messages in channels. ***This requires the server to be set up to allow such restrictions.***

### Squeak Censor
(disabled by default)  
Words from a list are replaced with squeaks. This is server-wide.
