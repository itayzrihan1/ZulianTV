# ZulianTV

**Automated media management system with Telegram bot control**

ZulianTV is a self-hosted media automation system that lets you request TV shows and movies via Telegram, automatically downloads them, and makes them available on your Jellyfin media server.

## Features

- Request TV shows and movies directly from Telegram
- Automatic download management via qBittorrent
- Organized library with Jellyfin media server
- Automatic subtitle downloads with Bazarr
- User authentication for bot access
- Smart search with multiple results
- Real-time status updates

## Architecture

ZulianTV consists of the following services:

- **Jellyfin** - Media server for streaming your content
- **Sonarr** - TV show management and automation
- **Radarr** - Movie management and automation
- **Prowlarr** - Indexer management (searches torrent sites)
- **Bazarr** - Automatic subtitle downloads
- **qBittorrent** - Torrent download client
- **ZulianTV Bot** - Custom Telegram bot for user interaction

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Telegram account
- Torrent indexer accounts (for Prowlarr)

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ZulianTV
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Get your Telegram Bot Token**
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot` and follow the instructions
   - Copy the bot token to `.env` file

4. **Get your Telegram User ID**
   - Message [@userinfobot](https://t.me/userinfobot) on Telegram
   - Copy your user ID to `.env` file under `ALLOWED_USERS`

5. **Start the services**
   ```bash
   docker-compose up -d
   ```

6. **Configure the services** (see detailed setup below)

## Detailed Configuration

### 1. Access Web UIs

After starting the containers, access each service:

- **Jellyfin**: http://localhost:8096
- **Sonarr**: http://localhost:8989
- **Radarr**: http://localhost:7878
- **Prowlarr**: http://localhost:9696
- **Bazarr**: http://localhost:6767
- **qBittorrent**: http://localhost:8080

### 2. Configure qBittorrent

1. Go to http://localhost:8080
2. Default credentials: `admin` / `adminadmin`
3. Change password in Settings
4. Set download path to `/downloads`

### 3. Configure Prowlarr

1. Go to http://localhost:9696
2. Add indexers (Settings → Indexers → Add Indexer)
3. Add Sonarr and Radarr as apps:
   - Settings → Apps → Add Application
   - Select Sonarr/Radarr
   - URL: `http://sonarr:8989` or `http://radarr:7878`
   - API Key: Get from Sonarr/Radarr (Settings → General)

### 4. Configure Sonarr

1. Go to http://localhost:8989
2. Add root folder: Settings → Media Management → Add Root Folder → `/tv`
3. Add download client:
   - Settings → Download Clients → Add → qBittorrent
   - Host: `qbittorrent`
   - Port: `8080`
   - Username/Password from qBittorrent
4. Copy API key from Settings → General
5. Add to `.env` file as `SONARR_API_KEY`

### 5. Configure Radarr

1. Go to http://localhost:7878
2. Add root folder: Settings → Media Management → Add Root Folder → `/movies`
3. Add download client:
   - Settings → Download Clients → Add → qBittorrent
   - Host: `qbittorrent`
   - Port: `8080`
   - Username/Password from qBittorrent
4. Copy API key from Settings → General
5. Add to `.env` file as `RADARR_API_KEY`

### 6. Configure Bazarr

1. Go to http://localhost:6767
2. Settings → Sonarr:
   - Enable: Yes
   - Address: `http://sonarr:8989`
   - API Key: From Sonarr
3. Settings → Radarr:
   - Enable: Yes
   - Address: `http://radarr:7878`
   - API Key: From Radarr
4. Add subtitle providers in Settings → Providers

### 7. Configure Jellyfin

1. Go to http://localhost:8096
2. Complete initial setup wizard
3. Add libraries:
   - Add Media Library → Shows → `/data/tvshows`
   - Add Media Library → Movies → `/data/movies`

### 8. Restart the Bot

After configuring API keys:
```bash
docker-compose restart zuliantv-bot
```

## Using the Bot

Start a chat with your bot on Telegram:

### Commands

- `/start` - Welcome message and command list
- `/help` - Show help information
- `/searchshow <name>` - Search for a TV show
- `/searchmovie <name>` - Search for a movie
- `/myshows` - List all your TV shows
- `/mymovies` - List all your movies

### Examples

```
/searchshow Breaking Bad
/searchmovie Inception
```

Or just type the name directly:
```
Breaking Bad
Inception movie
```

The bot will show you search results with buttons. Click to add to your library!

## Project Structure

```
ZulianTV/
├── docker-compose.yml          # Docker services configuration
├── .env                        # Environment variables (not in git)
├── .env.example               # Environment template
├── bot/                       # Telegram bot code
│   ├── bot.py                # Main bot logic
│   ├── config.py             # Configuration management
│   ├── sonarr_api.py         # Sonarr API client
│   ├── radarr_api.py         # Radarr API client
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # Bot container image
├── config/                    # Service configurations (auto-generated)
└── data/                      # Media and downloads (auto-generated)
    ├── downloads/            # Active downloads
    └── media/
        ├── tv/              # TV shows
        └── movies/          # Movies
```

## Troubleshooting

### Bot not responding
- Check bot logs: `docker-compose logs zuliantv-bot`
- Verify API keys in `.env` file
- Ensure all services are running: `docker-compose ps`

### Downloads not starting
- Check Prowlarr has indexers configured
- Verify qBittorrent is accessible from Sonarr/Radarr
- Check download client settings in Sonarr/Radarr

### Media not appearing in Jellyfin
- Wait for download to complete
- Check file permissions in `/data/media`
- Trigger library scan in Jellyfin

### Services not accessible
- Ensure ports are not in use: `netstat -an | findstr "8096 8989 7878"`
- Check Docker logs: `docker-compose logs <service-name>`

## Security Notes

- Change default passwords immediately
- Only share bot access with trusted users
- Consider adding VPN for download client
- Use reverse proxy with HTTPS for remote access
- Keep services behind firewall, only expose necessary ports

## Future Enhancements

- [ ] VPN integration for qBittorrent
- [ ] Reverse proxy with HTTPS
- [ ] Request approval system
- [ ] Download progress notifications
- [ ] Quality profile selection
- [ ] WhatsApp bot support
- [ ] User request history
- [ ] Admin commands

## Contributing

Feel free to open issues or submit pull requests!

## License

MIT License - feel free to use and modify as needed.
