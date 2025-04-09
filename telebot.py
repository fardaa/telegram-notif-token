import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    JobQueue,
    Job
)

# Ganti dengan token bot Anda dari BotFather
TELEGRAM_TOKEN = '8120636143:AAEjMIdKpl2vXtlYYvCVlOIQadbymoKEPlE'

# Ganti dengan chat ID Anda (didapat dari /start dan getUpdates)
CHAT_ID = '-4766084754'

# URL API GeckoTerminal
API_URL = 'https://api.geckoterminal.com/api/v2/networks/abstract/new_pools?page=1'

# Menyimpan pool yang sudah diberitahu
notified_pools = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk perintah /start"""
    await update.message.reply_text(
        'Bot dimulai! Anda akan menerima notifikasi untuk pool baru di jaringan Abstract.'
    )

    # Mulai job untuk polling data pool
    context.job_queue.run_repeating(
        check_new_pools,
        interval=300,   # setiap 5 menit
        first=10,       # mulai setelah 10 detik
        data=update.effective_chat.id  # kirim chat_id sebagai data
    )


async def check_new_pools(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cek pool baru dan kirim notifikasi ke Telegram"""
    chat_id = context.job.data  # Ambil chat_id yang dikirim via job

    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()

        pools = data.get('data', [])

        for pool in pools:
            pool_id = pool['id']
            attributes = pool['attributes']
            pool_name = attributes['name']
            pool_address = attributes['address']
            created_at = attributes['pool_created_at']

            if pool_id not in notified_pools:
                message = (
                    f"🚨 Pool Baru Ditemukan!\n"
                    f"🧪 Nama: {pool_name}\n"
                    f"📍 Alamat: {pool_address}\n"
                    f"🕒 Dibuat pada: {created_at}"
                )
                await context.bot.send_message(chat_id=chat_id, text=message)
                notified_pools.add(pool_id)

    except requests.exceptions.RequestException as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Gagal mengambil data dari API: {e}"
        )


def main() -> None:
    """Jalankan bot"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()


if __name__ == '__main__':
    main()
