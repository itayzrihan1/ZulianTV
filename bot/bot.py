"""
ZulianTV Telegram Bot - Main Bot Logic
Allows users to request TV shows and movies via Telegram
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import config
from sonarr_api import SonarrAPI
from radarr_api import RadarrAPI

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize API clients
sonarr = SonarrAPI()
radarr = RadarrAPI()


def is_authorized(user_id: int) -> bool:
    """Check if user is authorized to use the bot"""
    return user_id in config.ALLOWED_USERS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    if not is_authorized(user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    welcome_message = f"""
🎬 Welcome to ZulianTV, {user.first_name}!

I can help you add movies and TV shows to your Jellyfin library.

Available commands:
/searchshow <name> - Search for a TV show
/searchmovie <name> - Search for a movie
/myshows - List your TV shows
/mymovies - List your movies
/help - Show this help message

Just send me the name of what you want to watch!
"""
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message when the command /help is issued."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    help_text = """
🎬 ZulianTV Bot Commands:

📺 TV Shows:
/searchshow <name> - Search for a TV show
Example: /searchshow Breaking Bad

🎥 Movies:
/searchmovie <name> - Search for a movie
Example: /searchmovie Inception

📋 My Library:
/myshows - List all your TV shows
/mymovies - List all your movies

💡 Tips:
- You can also just type the name of a show/movie
- I'll help you choose if there are multiple matches
- I'll automatically download and organize everything!
"""
    await update.message.reply_text(help_text)


async def search_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search for a TV show"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    if not context.args:
        await update.message.reply_text("Please provide a show name. Example: /searchshow Breaking Bad")
        return

    query = ' '.join(context.args)
    await update.message.reply_text(f"🔍 Searching for '{query}'...")

    try:
        results = sonarr.search_series(query)

        if not results:
            await update.message.reply_text(f"No shows found for '{query}'. Try a different search term.")
            return

        # Show top 5 results
        keyboard = []
        for show in results[:5]:
            title = show.get('title', 'Unknown')
            year = show.get('year', 'N/A')
            tvdb_id = show.get('tvdbId')

            button_text = f"{title} ({year})"
            callback_data = f"add_show_{tvdb_id}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Found {len(results)} results. Select a show:",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error searching for show: {e}")
        await update.message.reply_text(f"Error searching for show: {str(e)}")


async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search for a movie"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    if not context.args:
        await update.message.reply_text("Please provide a movie name. Example: /searchmovie Inception")
        return

    query = ' '.join(context.args)
    await update.message.reply_text(f"🔍 Searching for '{query}'...")

    try:
        results = radarr.search_movies(query)

        if not results:
            await update.message.reply_text(f"No movies found for '{query}'. Try a different search term.")
            return

        # Show top 5 results
        keyboard = []
        for movie in results[:5]:
            title = movie.get('title', 'Unknown')
            year = movie.get('year', 'N/A')
            tmdb_id = movie.get('tmdbId')

            button_text = f"{title} ({year})"
            callback_data = f"add_movie_{tmdb_id}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Found {len(results)} results. Select a movie:",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error searching for movie: {e}")
        await update.message.reply_text(f"Error searching for movie: {str(e)}")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks for adding shows/movies"""
    query = update.callback_query
    await query.answer()

    if not is_authorized(query.from_user.id):
        await query.edit_message_text("Sorry, you are not authorized to use this bot.")
        return

    data = query.data

    try:
        if data.startswith('add_show_'):
            tvdb_id = int(data.split('_')[2])
            await query.edit_message_text("📺 Adding TV show to Sonarr...")

            result = sonarr.add_series_by_id(tvdb_id)
            title = result.get('title', 'Unknown')

            await query.edit_message_text(
                f"✅ '{title}' has been added!\n"
                f"Sonarr is now searching for episodes. You'll be notified when they're ready."
            )

        elif data.startswith('add_movie_'):
            tmdb_id = int(data.split('_')[2])
            await query.edit_message_text("🎥 Adding movie to Radarr...")

            result = radarr.add_movie_by_id(tmdb_id)
            title = result.get('title', 'Unknown')

            await query.edit_message_text(
                f"✅ '{title}' has been added!\n"
                f"Radarr is now searching for the movie. You'll be notified when it's ready."
            )

    except Exception as e:
        logger.error(f"Error in button callback: {e}")
        await query.edit_message_text(f"❌ Error: {str(e)}")


async def my_shows(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all TV shows in Sonarr"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    await update.message.reply_text("📺 Fetching your TV shows...")

    try:
        shows = sonarr.get_series_list()

        if not shows:
            await update.message.reply_text("No TV shows found in your library.")
            return

        message = f"📺 Your TV Shows ({len(shows)} total):\n\n"
        for show in shows[:20]:  # Limit to 20 to avoid message length issues
            title = show.get('title', 'Unknown')
            status = show.get('status', 'Unknown')
            message += f"• {title} - {status}\n"

        if len(shows) > 20:
            message += f"\n... and {len(shows) - 20} more"

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Error fetching shows: {e}")
        await update.message.reply_text(f"Error fetching shows: {str(e)}")


async def my_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all movies in Radarr"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    await update.message.reply_text("🎥 Fetching your movies...")

    try:
        movies = radarr.get_movies_list()

        if not movies:
            await update.message.reply_text("No movies found in your library.")
            return

        message = f"🎥 Your Movies ({len(movies)} total):\n\n"
        for movie in movies[:20]:  # Limit to 20 to avoid message length issues
            title = movie.get('title', 'Unknown')
            year = movie.get('year', 'N/A')
            status = "Downloaded" if movie.get('hasFile') else "Searching"
            message += f"• {title} ({year}) - {status}\n"

        if len(movies) > 20:
            message += f"\n... and {len(movies) - 20} more"

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Error fetching movies: {e}")
        await update.message.reply_text(f"Error fetching movies: {str(e)}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plain text messages - try to guess if it's a show or movie"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    text = update.message.text.strip()

    # Simple heuristic: if it contains "movie" or "film", search movies, otherwise TV
    if 'movie' in text.lower() or 'film' in text.lower():
        # Remove the word "movie" or "film" from the query
        query = text.lower().replace('movie', '').replace('film', '').strip()
        context.args = query.split()
        await search_movie(update, context)
    else:
        context.args = text.split()
        await search_show(update, context)


def main():
    """Start the bot"""
    # Validate configuration
    try:
        config.validate_config()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return

    # Create the Application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("searchshow", search_show))
    application.add_handler(CommandHandler("searchmovie", search_movie))
    application.add_handler(CommandHandler("myshows", my_shows))
    application.add_handler(CommandHandler("mymovies", my_movies))

    # Add callback handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))

    # Add message handler for plain text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Start the bot
    logger.info("ZulianTV Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
