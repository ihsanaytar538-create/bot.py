require('dotenv').config();

const {
  Client,
  GatewayIntentBits,
  AttachmentBuilder,
  EmbedBuilder
} = require('discord.js');

const path = require('path');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

client.once('ready', () => {
  console.log(`✅ Eingeloggt als ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
  if (message.author.bot) return;

  // Command: !play
  if (message.content === '!play') {

    // MP3 Datei Pfad
    const audioPath = path.join(__dirname, 'song.mp3');

    // Audio Datei
    const audioFile = new AttachmentBuilder(audioPath);

    // Schönes Embed
    const embed = new EmbedBuilder()
      .setTitle('🎵 Jetzt läuft')
      .setDescription('Travis Scott - FE!N')
      .setColor(0x2F3136);

    try {

      // Datei direkt im Chat senden
      await message.channel.send({
        embeds: [embed],
        files: [audioFile]
      });

    } catch (err) {
      console.error(err);
      message.reply('❌ Fehler beim Senden der Audio-Datei.');
    }
  }
});

client.login(process.env.TOKEN);
