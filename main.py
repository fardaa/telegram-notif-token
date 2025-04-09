import requests
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Ganti dengan token bot Anda dari BotFather
TELEGRAM_TOKEN = '8120636143:AAEjMIdKpl2vXtlYYvCVlOIQadbymoKEPlE'
# Ganti dengan chat ID Anda (bisa didapat dengan /getid di bot)
CHAT_ID = '-4766084754'

# URL API GeckoTerminal
API_URL = 'https://api.geckoterminal.com/api/v2/networks/abstract/new_pools?page=1'

# Variabel untuk menyimpan pool yang sudah diberitahu agar tidak ada duplikat
notified_pools = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk perintah /start"""
    await update.message.reply_text(
        'Bot telah dimulai! Anda akan menerima notifikasi untuk pool baru di jaringan Abstract.'
    )
    # Mulai proses polling API
    context.job_queue.run_repeating(check_new_pools, interval=300, first=10, context=update.message.chat_id)

async def check_new_pools(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fungsi untuk memeriksa pool baru dari API dan mengirim notifikasi"""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Memastikan request berhasil
        data = response.json()

        # Ambil daftar pool dari data
        pools = data.get('data', [])
        
        for pool in pools:
            pool_id = pool['id']
            pool_name = pool['attributes']['name']
            pool_address = pool['attributes']['address']
            created_at = pool['attributes']['pool_created_at']

            # Jika pool belum diberitahu sebelumnya
            if pool_id not in notified_pools:
                message = (
                    f"Pool Baru Ditemukan!\n"
                    f"Nama: {pool_name}\n"
                    f"Alamat: {pool_address}\n"
                    f"Dibuat pada: {created_at}"
                )
                await context.bot.send_message(chat_id=context.job.data, text=message)
                notified_pools.add(pool_id)  # Tandai pool sebagai sudah diberitahu

    except requests.exceptions.RequestException as e:
        error_message = f"Gagal mengambil data dari API: {e}"
        await context.bot.send_message(chat_id=context.job.data, text=error_message)

def main() -> None:
    """Fungsi utama untuk menjalankan bot"""
    # Inisialisasi bot
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Tambahkan handler untuk perintah /start
    application.add_handler(CommandHandler("start", start))

    # Jalankan bot
    application.run_polling()

if __name__ == '__main__':
    main()