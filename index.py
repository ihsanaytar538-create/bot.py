const { Client, GatewayIntentBits } = require("discord.js");
const {
    joinVoiceChannel,
    createAudioPlayer,
    createAudioResource,
    AudioPlayerStatus
} = require("@discordjs/voice");

const ytdl = require("ytdl-core");

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildVoiceStates,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

const prefix = "!";

client.on("messageCreate", async (message) => {
    if (!message.content.startsWith(prefix) || message.author.bot) return;

    const args = message.content.split(" ");
    const command = args[0];

    // !play <youtube link>
    if (command === "!play") {
        const url = args[1];
        if (!url) return message.reply("Bitte YouTube-Link angeben!");

        const voiceChannel = message.member.voice.channel;
        if (!voiceChannel) return message.reply("Du bist in keinem Voice-Channel!");

        const connection = joinVoiceChannel({
            channelId: voiceChannel.id,
            guildId: message.guild.id,
            adapterCreator: message.guild.voiceAdapterCreator
        });

        const stream = ytdl(url, { filter: "audioonly" });
        const resource = createAudioResource(stream);
        const player = createAudioPlayer();

        player.play(resource);
        connection.subscribe(player);

        player.on(AudioPlayerStatus.Playing, () => {
            message.channel.send("🎶 Musik wird abgespielt!");
        });

        player.on(AudioPlayerStatus.Idle, () => {
            connection.destroy();
        });
    }

    // !stop
    if (command === "!stop") {
        const voiceChannel = message.member.voice.channel;
        if (!voiceChannel) return;

        const connection = joinVoiceChannel({
            channelId: voiceChannel.id,
            guildId: message.guild.id,
            adapterCreator: message.guild.voiceAdapterCreator
        });

        connection.destroy();
        message.channel.send("⏹️ Musik gestoppt!");
    }
});

client.login("DEIN_BOT_TOKEN");
