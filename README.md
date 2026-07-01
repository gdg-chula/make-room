# MakeRoom - Prototype

MakeRoom is a self-hosted Discord bot designed to **manage temporary voice channel**. It automatically creates and removes voice channels as needed, helping to keep your server organized and clutter-free.

## ✨ Features

* **Dynamic Voice Channels:** Users join a specific creation channel (`+ Create Room`), and the bot instantly moves them into their own personalized, temporary voice channel.
* **Auto-Cleanup:** Once everyone leaves a temporary room, the bot automatically deletes it to keep your channel list pristine.
* **Room Privacy Controls:** Room creators are provided with a persistent UI button to toggle their room's visibility between public and private. Users already inside a private room retain text-chat access.
* **Spam Honeypot:** A trap text channel (`#dusty-locker`) which lure the spam user. If user send a message to the honeypot channel. the bot automatically bans and remove all the messages.

## 🛠️ Prerequisites & Discord Setup

Before running the bot, you must configure your bot in the [Discord Developer Portal](https://discord.com/developers/applications):

1.  **Privileged Gateway Intents:** Make sure to toggle **ON** the following intents in the "Bot" tab:
    * Message Content Intent
    * Server Members Intent
2.  **Bot Permissions:** When generating your OAuth2 invite link, ensure the bot is granted the following permissions:
    * `Manage Channels` (To create/delete categories and voice rooms)
    * `Manage Roles` (To modify channel view permissions)
    * `Send Messages` & `Embed Links` (For UI controls and alerts)
    * `Ban Members` (For the honeypot feature)

## Quick Deployment with Docker

Get MakeRoom up and running in minutes using Docker Compose:

1.  **Create a `.env` file** in the root directory and add your Discord bot token:
    ```
    DISCORD_TOKEN=your_discord_token_here
    ```
2.  **Ensure Docker Engine is running** on your system.
3.  **Run the bot** with Docker Compose:
    ```bash
    docker compose up -d
    ```

That's it! Your MakeRoom bot should now be online and ready to manage voice channels.

## 📄 License

This project is licensed under the [**MIT License**](https://opensource.org/licenses/MIT).