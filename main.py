import yfinance as yf
import pandas as pd
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# TOKEN LANGSUNG HARDCODE - GANTI NANTI KALO UDAH JALAN
TOKEN_BOT = "8780347773:AAGhPuoF1ivhqJeGC-nzDNIrP3L2n3tpcKs"

# 100 SAHAM UNGGULAN IDX - WAJIB PAKE.JK BUAT YFINANCE
SAHAM_UNGGULAN = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "UNVR.JK", "ICBP.JK", "INDF.JK", "KLBF.JK", "GGRM.JK",
    "HMSP.JK", "INCO.JK", "ANTM.JK", "PTBA.JK", "ADRO.JK", "ITMG.JK", "PGAS.JK", "MEDC.JK", "AKRA.JK", "MNCN.JK",
    "SCMA.JK", "EMTK.JK", "TOWR.JK", "TBIG.JK", "EXCL.JK", "ISAT.JK", "FREN.JK", "JSMR.JK", "WIKA.JK", "PTPP.JK",
    "WSKT.JK", "ADHI.JK", "SMGR.JK", "INTP.JK", "SMBR.JK", "SMGR.JK", "INKP.JK", "TKIM.JK", "AALI.JK", "LSIP.JK",
    "SIMP.JK", "SSMS.JK", "TAPG.JK", "BWPT.JK", "DSNG.JK", "UNTR.JK", "HEXE.JK", "WEHA.JK", "ASGR.JK", "AUTO.JK",
    "GJTL.JK", "IMAS.JK", "INDS.JK", "LPIN.JK", "MASA.JK", "NIPS.JK", "PRAS.JK", "SULT.JK", "BRIS.JK", "BTPS.JK",
    "PNBN.JK", "BNGA.JK", "BNLI.JK", "NISP.JK", "BBTN.JK", "BDMN.JK", "AGRO.JK", "BEKS.JK", "MAYA.JK", "BACA.JK",
    "BABP.JK", "BGTG.JK", "BCIC.JK", "BKSW.JK", "BSWD.JK", "BVIC.JK", "DNAR.JK", "INPC.JK", "MCOR.JK", "PNBS.JK",
    "SDRA.JK", "AMAR.JK", "ARTO.JK", "BBMD.JK", "BBSI.JK", "BINA.JK", "BMAS.JK", "BSIM.JK", "BUKK.JK", "CEKA.JK",
    "CLEO.JK", "CO.JK", "DLTA.JK", "GOTO.JK", "BUKA.JK", "BIRD.JK", "BIPI.JK", "ELSA.JK", "ESSA.JK", "HRUM.JK"
]

def hitung_rsi(series, periode=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periode).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periode).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def hitung_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def analisa_saham(ticker):
    try:
        saham = yf.Ticker(ticker)
        df = saham.history(period="3mo")
        if df.empty or len(df) < 30:
            return None

        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = hitung_rsi(df['Close'])
        macd, signal, hist = hitung_macd(df['Close'])
        df['MACD'] = macd
        df['Signal'] = signal

        harga = df['Close'].iloc[-1]
        ma20 = df['MA20'].iloc[-1]
        ma50 = df['MA50'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        macd_val = df['MACD'].iloc[-1]
        signal_val = df['Signal'].iloc[-1]
        vol = df['Volume'].iloc[-1]
        avg_vol = df['Volume'].rolling(window=20).mean().iloc[-1]

        skor = 0
        alasan = []

        if harga > ma20 > ma50:
            skor += 2
            alasan.append("Uptrend MA20>MA50")
        if rsi < 30:
            skor += 2
            alasan.append("RSI Oversold")
        elif rsi > 50 and rsi < 70:
            skor += 1
            alasan.append("RSI Kuat")
        if macd_val > signal_val:
            skor += 2
            alasan.append("MACD Bullish Cross")
        if vol > avg_vol * 1.5:
            skor += 1
            alasan.append("Volume Meledak")

        if skor >= 4:
            return {
                "ticker": ticker.replace(".JK", ""),
                "harga": harga,
                "skor": skor,
                "alasan": ", ".join(alasan),
                "rsi": round(rsi, 1)
            }
        return None
    except:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Bot Dewa IDX v1.3.2 Konglo Aktif!\n\n"
        "Command:\n"
        "/praara - Screener 100 saham unggulan\n"
        "/harga KODE - Cek harga saham, contoh: /harga BBCA\n"
        "/sinyal KODE - Analisa lengkap 1 saham"
    )

async def harga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Pake format: /harga BBCA")
        return
    kode = context.args[0].upper() + ".JK"
    try:
        saham = yf.Ticker(kode)
        data = saham.history(period="1d")
        if data.empty:
            await update.message.reply_text(f"Saham {kode.replace('.JK','')} nggak ketemu bro")
            return
        harga = data['Close'].iloc[-1]
        await update.message.reply_text(f"Harga {kode.replace('.JK','')}: Rp {harga:,.0f}")
    except:
        await update.message.reply_text("Error ambil data. Coba lagi")

async def sinyal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Pake format: /sinyal BBCA")
        return
    kode = context.args[0].upper() + ".JK"
    await update.message.reply_text(f"Sedang analisa {kode.replace('.JK','')}... Sabar 3 detik")
    hasil = analisa_saham(kode)
    if hasil:
        teks = f"📈 SINYAL {hasil['ticker']}\nHarga: Rp {hasil['harga']:,.0f}\nSkor: {hasil['skor']}/7\nRSI: {hasil['rsi']}\nAlasan: {hasil['alasan']}"
    else:
        teks = f"Nggak ada sinyal kuat buat {kode.replace('.JK','')} sekarang. Coba /praara buat cari yg lain"
    await update.message.reply_text(teks)

async def praara(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Screening 100 Saham Unggulan IDX... Ini 30-60 detik bro, sabar...")
    hasil_sinyal = []
    for ticker in SAHAM_UNGGULAN:
        res = analisa_saham(ticker)
        if res:
            hasil_sinyal.append(res)

    if not hasil_sinyal:
        await update.message.reply_text("Zonk bro 😭 Nggak ada saham yg lolos screener hari ini. Market lagi jelek.")
        return

    hasil_sinyal = sorted(hasil_sinyal, key=lambda x: x['skor'], reverse=True)[:5]
    teks = "🔥 TOP 5 SAHAM SINYAL KUAT HARI INI 🔥\n\n"
    for i, s in enumerate(hasil_sinyal, 1):
        teks += f"{i}. {s['ticker']} - Rp {s['harga']:,.0f}\n Skor: {s['skor']}/7 | RSI: {s['rsi']}\n {s['alasan']}\n\n"
    teks += "Disclaimer: Bukan ajakan beli. DYOR!"
    await update.message.reply_text(teks)

if __name__ == '__main__':
    print("Bot Dewa IDX v1.3.2 Konglo jalan...")
    app = ApplicationBuilder().token(TOKEN_BOT).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("harga", harga))
    app.add_handler(CommandHandler("sinyal", sinyal))
    app.add_handler(CommandHandler("praara", praara))

    app.run_polling()
