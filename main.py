import yfinance as yf
import pandas as pd
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import time

# TOKEN BOT LU - RESET SETELAH INI YA
TOKEN_BOT = "8780347773:AAGhPuoF1ivhqJeGC-nzDNIrP3L2n3tpcKs"

# LIST 100 SAHAM: LQ45 + IDX30 + SAHAM KONGLO GORENGAN
LIST_SAHAM = [
    # LQ45 Bluechip
    'BBCA', 'BBRI', 'BMRI', 'TLKM', 'ASII', 'UNVR', 'GOTO', 'AMRT', 'BBNI', 'KLBF',
    'MDKA', 'PGAS', 'ADRO', 'ANTM', 'INDF', 'UNTR', 'ICBP', 'INCO', 'SMGR', 'TOWR',
    'BRPT', 'AKRA', 'EXCL', 'MNCN', 'PTBA', 'ITMG', 'CPIN', 'TKIM', 'GGRM', 'INTP',

    # Grup Bakrie & Co
    'BUMI', 'DEWA', 'ELSA', 'BNBR', 'BRMS', 'ENRG', 'BTEL', 'SULI',

    # Grup Salim & Astra Lainnya
    'AMAR', 'AISA', 'CMRY', 'JPFA', 'MAIN', 'MYOR',

    # Grup Sinar Mas & Sinarmas
    'BSDE', 'SMAR', 'TPIA', 'SMMA', 'SIMA', 'DSSA',

    # Grup Prajogo Pangestu
    'BREN', 'TPIA', 'PTRO', 'CUAN', 'CDIA',

    # BUMN Karya & Energi
    'WIKA', 'WSKT', 'ADHI', 'PTPP', 'KRAS', 'ANTM', 'TINS', 'PGAS', 'ELSA', 'MEDC',

    # Konglo Hapsoro & Lainnya
    'BUVA', 'BIPI', 'HUMI', 'OASA', 'INDY', 'DOID', 'FREN', 'ISAT', 'EMTK',

    # Saham Gorengan Rame
    'BABP', 'BANK', 'BEBS', 'BOLA', 'CITA', 'DILD', 'FMII', 'GEMA', 'GPRA', 'HDFA',
    'IPCM', 'JSMR', 'KIJA', 'LINK', 'LPKR', 'MAPI', 'MIRA', 'MTDL', 'PNLF', 'PWON',
    'RAJA', 'SAME', 'SCMA', 'SRTG', 'SSIA', 'TBLA', 'TOTL', 'ULTJ', 'WEGE', 'WIFI'
]

# ===== FUNGSI INDIKATOR =====

def hitung_rsi(data, periode=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periode).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periode).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def hitung_ma(data, periode):
    return data['Close'].rolling(window=periode).mean()

# ===== FUNGSI SCREENER DENGAN DELAY AMAN =====

def screener_oversold(list_saham, batas_rsi=30):
    hasil = []
    for i, kode in enumerate(list_saham):
        try:
            df = yf.Ticker(f"{kode}.JK").history(period="3mo")
            if len(df) < 20: continue
            rsi = hitung_rsi(df).iloc[-1]
            harga = df['Close'].iloc[-1]
            if rsi < batas_rsi:
                hasil.append(f"{kode}: Rp{harga:,.0f} | RSI {rsi:.1f}")
            time.sleep(1) # DELAY 1 DETIK BIAR AMAN
        except: continue
    return hasil

def screener_bsjp(list_saham):
    hasil = []
    for kode in list_saham:
        try:
            df = yf.Ticker(f"{kode}.JK").history(period="5d")
            if len(df) < 5: continue
            harga_turun = df['Close'].iloc[-1] < df['Close'].iloc[-3]
            vol_boom = df['Volume'].iloc[-1] > df['Volume'].mean() * 1.5
            rsi = hitung_rsi(df).iloc[-1]
            if harga_turun and vol_boom and rsi < 45:
                hasil.append(f"{kode}: Rp{df['Close'].iloc[-1]:,.0f} | Vol +{df['Volume'].iloc[-1]/df['Volume'].mean():.1f}x")
            time.sleep(1)
        except: continue
    return hasil

def screener_scalping(list_saham):
    hasil = []
    for kode in list_saham:
        try:
            df = yf.Ticker(f"{kode}.JK").history(period="1mo")
            if len(df) < 20: continue
            ma5 = hitung_ma(df, 5).iloc[-1]
            ma20 = hitung_ma(df, 20).iloc[-1]
            rsi = hitung_rsi(df).iloc[-1]
            vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
            if ma5 > ma20 and 35 < rsi < 65 and vol_ratio > 1.2:
                hasil.append(f"{kode}: Rp{df['Close'].iloc[-1]:,.0f} | MA5>MA20 | Vol {vol_ratio:.1f}x")
            time.sleep(1)
        except: continue
    return hasil

def screener_swing(list_saham):
    hasil = []
    for kode in list_saham:
        try:
            df = yf.Ticker(f"{kode}.JK").history(period="6mo")
            if len(df) < 50: continue
            ma20 = hitung_ma(df, 20)
            ma50 = hitung_ma(df, 50)
            rsi = hitung_rsi(df)
            golden_cross = ma20.iloc[-1] > ma50.iloc[-1] and ma20.iloc[-2] < ma50.iloc[-2]
            di_atas_ma50 = df['Close'].iloc[-1] > ma50.iloc[-1]
            rsi_mantul = 40 < rsi.iloc[-1] < 60 and rsi.iloc[-2] < rsi.iloc[-1]
            if golden_cross and di_atas_ma50 and rsi_mantul:
                hasil.append(f"{kode}: Rp{df['Close'].iloc[-1]:,.0f} | Golden Cross")
            time.sleep(1)
        except: continue
    return hasil

def screener_daytrade(list_saham):
    hasil = []
    for kode in list_saham:
        try:
            df = yf.Ticker(f"{kode}.JK").history(period="1mo")
            if len(df) < 20: continue
            high_1bulan = df['High'].iloc[:-1].max()
            harga_now = df['Close'].iloc[-1]
            vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
            if harga_now > high_1bulan and vol_ratio > 1.8:
                hasil.append(f"{kode}: Rp{harga_now:,.0f} | Breakout | Vol {vol_ratio:.1f}x")
            time.sleep(1)
        except: continue
    return hasil

# ===== COMMAND TELEGRAM =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks = "*Bot Dewa IDX v1.3 - Konglo Edition* 🔥\n\n*Scan 100 Saham:*\n/screener - Oversold RSI<30\n/bsjp - Akumulasi Bandar\n/scalping - Sinyal Cepat\n/swing - Golden Cross\n/daytrade - Breakout\n\n/harga BUMI - Cek harga\n\n_Delay 15m. DYOR._"
    await update.message.reply_text(teks, parse_mode='Markdown')

async def harga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Contoh: /harga PTRO")
        return
    kode = context.args[0]
    msg = await update.message.reply_text(f"Lagi ambil data {kode.upper()}...")
    try:
        saham = yf.Ticker(f"{kode.upper()}.JK")
        data = saham.history(period="2d")
        harga_now = data['Close'].iloc[-1]
        persen = ((harga_now - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
        volume = data['Volume'].iloc[-1]
        hasil = f"*{kode.upper()}*\nHarga: Rp{harga_now:,.0f}\nChange: {persen:+.2f}%\nVolume: {volume:,.0f}\n_Delay 15m_"
        await msg.edit_text(hasil, parse_mode='Markdown')
    except:
        await msg.edit_text("Kode saham nggak ketemu atau lagi suspend.")

async def cmd_screener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Scan 100 saham Oversold RSI<30... Sabar ya 2 menitan 🔍")
    hasil = screener_oversold(LIST_SAHAM)
    teks = "*Oversold RSI<30:*\n\n" + "\n".join(hasil) if hasil else "Nihil. Market lagi kuat."
    await msg.edit_text(teks + "\n\n_DYOR_", parse_mode='Markdown')

async def cmd_bsjp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Scan 100 saham Sinyal BSJP... Sabar ya 2 menitan 🔍")
    hasil = screener_bsjp(LIST_SAHAM)
    teks = "*Sinyal BSJP Akumulasi:*\n\n" + "\n".join(hasil) if hasil else "Nihil. Bandar lagi diem."
    await msg.edit_text(teks + "\n\n_DYOR_", parse_mode='Markdown')

async def cmd_scalping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Scan 100 saham Sinyal Scalping... Sabar ya 2 menitan 🔍")
    hasil = screener_scalping(LIST_SAHAM)
    teks = "*Sinyal Scalping:*\n\n" + "\n".join(hasil) if hasil else "Nihil. Setup belum ada."
    await msg.edit_text(teks + "\n\n_DYOR_", parse_mode='Markdown')

async def cmd_swing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Scan 100 saham Sinyal Swing... Sabar ya 2 menitan 🔍")
    hasil = screener_swing(LIST_SAHAM)
    teks = "*Sinyal Swing Golden Cross:*\n\n" + "\n".join(hasil) if hasil else "Nihil. Belum ada golden cross."
    await msg.edit_text(teks + "\n\n_DYOR_", parse_mode='Markdown')

async def cmd_daytrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Scan 100 saham Breakout... Sabar ya 2 menitan 🔍")
    hasil = screener_daytrade(LIST_SAHAM)
    teks = "*Sinyal Daytrade Breakout:*\n\n" + "\n".join(hasil) if hasil else "Nihil. Nggak ada yg breakout."
    await msg.edit_text(teks + "\n\n_DYOR_", parse_mode='Markdown')

# ===== JALANIN BOT =====
if __name__ == '__main__':
    print("Bot Dewa IDX v1.3 Konglo jalan...")
    app = ApplicationBuilder().token(TOKEN_BOT).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("harga", harga))
    app.add_handler(CommandHandler("screener", cmd_screener))
    app.add_handler(CommandHandler("bsjp", cmd_bsjp))
    app.add_handler(CommandHandler("scalping", cmd_scalping))
    app.add_handler(CommandHandler("swing", cmd_swing))
    app.add_handler(CommandHandler("daytrade", cmd_daytrade))
    app.run_polling()
