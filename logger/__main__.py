import os
import sys
import logging
import datetime

import discord

logging.basicConfig(level=logging.DEBUG, handlers=[logging.FileHandler("logger.log"), logging.StreamHandler()])
LOG = logging.getLogger(__name__)

logging.getLogger("discord").setLevel(logging.INFO)
logging.getLogger("websockets").setLevel(logging.INFO)


LOGGING_CHANNELS = {
    561865523651149834: 561876621380812811,
}

client = discord.Client()

@client.event
async def on_message(message):
    if message.guild is None:
        return
    if message.guild.id not in LOGGING_CHANNELS:
        return
    logging_channel_id = LOGGING_CHANNELS[message.guild.id]
    if message.channel.id == logging_channel_id:
        return

    logging_channel = message.guild.get_channel(logging_channel_id)
    if logging_channel is None:
        LOG.error(f"Cannot find channel {logging_channel} in guild {message.guild.id}")
        return

    embed = discord.Embed(
            title="Message sent",
            type="rich",
            description=message.content,
            timestamp=message.created_at,
            color=discord.Color.from_rgb(0, 186, 9),
    )
    embed.add_field(name="Sender Name", value=f"{message.author.name}#{message.author.discriminator}")
    embed.add_field(name="Sender ID", value=message.author.id)
    embed.add_field(name="Channel Name", value=message.channel.name)
    embed.add_field(name="Channel ID", value=message.channel.id)
    embed.add_field(name="Message ID", value=message.id)

    await logging_channel.send(embed=embed)

@client.event
async def on_raw_message_edit(payload):
    data = payload.data

    if "guild_id" not in data:
        return
    if "channel_id" not in data:
        return
    if "content" not in data:
        return
    if "edited_timestamp" not in data:
        return
    # Note: This assumes that the author section always has the same structure.
    if "author" not in data:
        return

    guild_id = int(data["guild_id"])
    channel_id = int(data["channel_id"])
    channel = client.get_channel(channel_id)

    logging_channel_id = LOGGING_CHANNELS[guild_id]
    if channel_id == logging_channel_id:
        return

    logging_channel = client.get_channel(logging_channel_id)
    if logging_channel is None:
        LOG.error(f"Cannot find channel {logging_channel} in guild {message.guild.id}")
        return
    
    embed = discord.Embed(
            title="Message edited",
            type="rich",
            description=data["content"],
            timestamp=discord.utils.parse_time(data["edited_timestamp"]),
            color=discord.Color.from_rgb(239, 231, 4),
    )
    embed.add_field(name="Sender Name", value=f"{data['author']['username']}#{data['author']['discriminator']}")
    embed.add_field(name="Sender ID", value=data["author"]["id"])
    embed.add_field(name="Channel Name", value=channel.name)
    embed.add_field(name="Channel ID", value=channel.id)
    embed.add_field(name="Message ID", value=data["id"])
    embed.add_field(name="Message Time", value=data["timestamp"])

    await logging_channel.send(embed=embed)



@client.event
async def on_raw_message_delete(payload):
    if payload.guild_id is None:
        return

    
    logging_channel_id = LOGGING_CHANNELS[payload.guild_id]
    if payload.channel_id == logging_channel_id:
        return

    logging_channel = client.get_channel(logging_channel_id)
    if logging_channel is None:
        LOG.error(f"Cannot find channel {logging_channel} in guild {message.guild.id}")
        return

    embed = discord.Embed(
            title="Message deleted",
            type="rich",
            timestamp=datetime.datetime.now(),
            color=discord.Color.from_rgb(188, 0, 0),
    )
    embed.add_field(name="Message ID", value=payload.message_id)

    await logging_channel.send(embed=embed)

# TODO implement on_raw_bulk_message_delete


    


@client.event
async def on_ready():
    LOG.info("Logged in as {}#{}-{}".format(client.user.name, client.user.discriminator, client.user.id))


if "DISCORD_TOKEN" not in os.environ:
    LOG.error("No discord token environment variable. Exiting")
    sys.exit()
else:
    client.run(os.environ["DISCORD_TOKEN"])

