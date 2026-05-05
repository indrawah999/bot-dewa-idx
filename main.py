import os
import yfinance as yf
import pandas as pd
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# TOKEN AMBIL DARI RAILWAY VARIABLES - JANGAN TARUH DI SINI
TOKEN_BOT = os.environ.get('8780347773:AAGhPuoF1ivhqJeGC-nzDNIrP3L2n3tpcKs')

# 100 SAHAM UNGGULAN IDX - WAJIB PAKE.JK BUAT YFINANCE
SAHAM_UNGGULAN = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "UNVR.JK", "ICBP.JK", "INDF.JK", "KLBF.JK", "GGRM.JK",
    "HMSP.JK", "INCO.JK", "ANTM.JK", "PTBA.JK", "ADRO.JK", "ITMG.JK", "PGAS.JK", "MEDC.JK", "AKRA.JK", "MNCN.JK",
    "SCMA.JK", "EMTK.JK", "TOWR.JK", "TBIG.JK", "EXCL.JK", "ISAT.JK", "FREN.JK", "JSMR.JK", "WIKA.JK", "PTPP.JK",
    "WSKT.JK", "ADHI.JK", "SMGR.JK", "INTP.JK", "SMBR.JK", "Semen.JK", "INKP.JK", "TKIM.JK", "AALI.JK", "LSIP.JK",
    "SIMP.JK", "SSMS.JK", "TAPG.JK", "BWPT.JK", "DSNG.JK", "UNTR.JK", "HEXE.JK", "WEHA.JK", "ASGR.JK", "AUTO.JK",
    "GJTL.JK", "IMAS.JK", "INDS.JK", "LPIN.JK", "MASA.JK", "NIPS.JK", "PRAS.JK", "SULT.JK", "BRIS.JK", "BTPS.JK",
    "PNBN.JK", "BNGA.JK", "BNLI.JK", "NISP.JK", "BBTN.JK", "BDMN.JK", "AGRO.JK", "BEKS.JK", "MAYA.JK", "BACA.JK",
    "BABP.JK", "BGTG.JK", "BCIC.JK", "BKSW.JK", "BSWD.JK", "BVIC.JK", "DNAR.JK", "INPC.JK", "MCOR.JK", "PNBS.JK",
    "SDRA.JK", "AMAR.JK", "ARTO.JK", "BBMD.JK", "BBSI.JK", "BINA.JK", "BMAS.JK", "BSIM.JK", "BUKK.JK", "CEKA.JK",
    "CLEO.JK", "CO.JK", "DLTA.JK", "GOTO.JK", "BUKA.JK", "BIRD.JK", "BIPI.JK", "ELSA.JK", "ESSA.JK", "HRUM.JK"
]

def hitung_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def bersih_kode(kode):
    """Hapus.JK biar tampilan bersih"""
    return kode.replace('.JK', '')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pesan = """Bot Dewa IDX v1.3.2 - Konglo Edition 🔥

Scan 100 Saham:
/screener - Oversold RSI<30
/bsjp - Akumulasi Bandar
/scalping - Sinyal Cepat
/swing - Golden Cross
/daytrade - Breakout
/praara - Potensi ARA Besok 🔥
/harga BBCA - Cek harga

Delay 15m. DYOR."""
    await update.message.reply_text(pesan)

async def harga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kode_input = context.args[0].upper()
        # User boleh ketik BBCA atau BBCA.JK, kita tambahin.JK otomatis
        if not kode_input.endswith('.JK'):
            kode_yf = kode_input + '.JK'
        else:
            kode_yf = kode_input

        ticker = yf.Ticker(kode_yf)
        info = ticker.info
        hist = ticker.history(period="2d")
        if len(hist) < 2:
            await update.message.reply_text("Data saham nggak ketemu bro")
            return

        harga_now = hist['Close'].iloc[-1]
        harga_prev = hist['Close'].iloc[-2]
        change = ((harga_now - harga_prev) / harga_prev) * 100
        volume = hist['Volume'].iloc[-1]

        # Pake bersih_kode() biar output nggak ada.JK
        nama_saham = bersih_kode(kode_yf)
        pesan = f"*{info.get('longName', nama_saham)}*\n"
        pesan += f"Kode: {nama_saham}\n"
        pesan += f"Harga: Rp{harga_now:,.0f}\n"
        pesan += f"Change: {change:+.2f}%\n"
        pesan += f"Volume: {volume:,.0f}\n"
        pesan += f"Delay 15m"
        await update.message.reply_text(pesan, parse_mode='Markdown')
    except:
        await update.message.reply_text("Format salah. Contoh: /harga BBCA")

async def screener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Scan Oversold RSI<30...")
    hasil = []
    for kode in SAHAM_UNGGULAN[:100]:
        try:
            data = yf.Ticker(kode).history(period="1mo")
            rsi = hitung_rsi(data['Close']).iloc[-1]
            if rsi < 30:
                hasil.append(f"📉 {bersih_kode(kode)} - RSI: {rsi:.1f}")
            if len(hasil) >= 10: break
        except: continue
    pesan = "🔥 **SAHAM OVERSOLD RSI<30**\n\n" + "\n".join(hasil) if hasil else "Nihil bosku."
    await update.message.reply_text(pesan, parse_mode='Markdown')

async def pra_ara(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ Scan 100 Saham Pra-ARA...\nCari +15% sd +24% + Volume Jebol")
    hasil = []
    for kode in SAHAM_UNGGULAN[:100]:
        try:
            ticker = yf.Ticker(kode)
            hist = ticker.history(period="25d")
            if len(hist) < 21: continue

            harga_now = hist['Close'].iloc[-1]
            harga_prev = hist['Close'].iloc[-2]
            change = ((harga_now - harga_prev) / harga_prev) * 100
            vol_now = hist['Volume'].iloc[-1]
            vol_avg20 = hist['Volume'].iloc[-21:-1].mean()

            # Syarat Pra-ARA: Naik 15-24.5% + Volume > 3x rata2
            if 15 <= change < 24.5 and vol_now > vol_avg20 * 3 and vol_avg20 > 0:
                hasil.append(f"🔥 {bersih_kode(kode)}: +{change:.1f}% | Vol {vol_now/vol_avg20:.1f}x")

            if len(hasil) >= 10: break
        except: continue

    if hasil:
        pesan = "🚀 **SINYAL PRA-ARA TERDETEKSI**\nDelay 15m\n\n" + "\n".join(hasil) + "\n\n*Besok potensi ARA. DYOR.*"
    else:
        pesan = "😴 Belum ada saham Pra-ARA hari ini.\nCoba cek lagi jam 15:30 WIB."
    await update.message.reply_text(pesan, parse_mode='Markdown')

# Fungsi lain biar nggak error
async def bsjp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fitur BSJP coming soon")

async def scalping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fitur Scalping coming soon")

async def swing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fitur Swing coming soon")

async def daytrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fitur Daytrade coming soon")

app = ApplicationBuilder().token(TOKEN_BOT).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("harga", harga))
app.add_handler(CommandHandler("screener", screener))
app.add_handler(CommandHandler("praara", pra_ara))
app.add_handler(CommandHandler("bsjp", bsjp))
app.add_handler(CommandHandler("scalping", scalping))
app.add_handler(CommandHandler("swing", swing))
app.add_handler(CommandHandler("daytrade", daytrade))

print("Bot Dewa IDX v1.3.2 Konglo jalan...")
app.run_polling()
