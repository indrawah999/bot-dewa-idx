import yfinance as yf
import pandas as pd
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# TOKEN LANGSUNG HARDCODE - GANTI NANTI KALO UDAH JALAN
TOKEN_BOT = "8780347773:AAGhPuoF1ivhqJeGC-nzDNIrP3L2n3tpcKs"

# 150 SAHAM UNGGULAN + KONGLO + GORENGAN TRENDING
SAHAM_UNGGULAN = [
    # Blue Chip LQ45
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "UNVR.JK", "ICBP.JK", "INDF.JK", "KLBF.JK", "GGRM.JK",
    "HMSP.JK", "INCO.JK", "ANTM.JK", "PTBA.JK", "ADRO.JK", "ITMG.JK", "PGAS.JK", "MEDC.JK", "AKRA.JK", "MNCN.JK",
    "SCMA.JK", "EMTK.JK", "TOWR.JK", "TBIG.JK", "EXCL.JK", "ISAT.JK", "FREN.JK", "JSMR.JK", "WIKA.JK", "PTPP.JK",
    "WSKT.JK", "ADHI.JK", "SMGR.JK", "INTP.JK", "SMBR.JK", "INKP.JK", "TKIM.JK", "AALI.JK", "LSIP.JK",
    "SIMP.JK", "SSMS.JK", "TAPG.JK", "BWPT.JK", "DSNG.JK", "UNTR.JK", "HEXE.JK", "WEHA.JK", "ASGR.JK", "AUTO.JK",
    "GJTL.JK", "IMAS.JK", "INDS.JK", "LPIN.JK", "MASA.JK", "NIPS.JK", "PRAS.JK", "SULT.JK", "BRIS.JK", "BTPS.JK",
    "PNBN.JK", "BNGA.JK", "BNLI.JK", "NISP.JK", "BBTN.JK", "BDMN.JK", "AGRO.JK", "BEKS.JK", "MAYA.JK", "BACA.JK",
    "BABP.JK", "BGTG.JK", "BCIC.JK", "BKSW.JK", "BSWD.JK", "BVIC.JK", "DNAR.JK", "INPC.JK", "MCOR.JK", "PNBS.JK",
    "SDRA.JK", "AMAR.JK", "ARTO.JK", "BBMD.JK", "BBSI.JK", "BINA.JK", "BMAS.JK", "BSIM.JK", "BUKK.JK", "CEKA.JK",
    "CLEO.JK", "CO.JK", "DLTA.JK", "GOTO.JK", "BUKA.JK", "BIRD.JK", "BIPI.JK", "ELSA.JK", "ESSA.JK", "HRUM.JK",

    # SAHAM KONGLO GORENGAN
    "PTRO.JK", "BUMI.JK", "BRMS.JK", "DEWA.JK", "ENRG.JK", "PK.JK", "DOID.JK", "INDY.JK", "ABMM.JK", "BYAN.JK",
    "CUAN.JK", "TPIA.JK", "BREN.JK", "CDIA.JK", "PANI.JK", "CBDK.JK", "PNLF.JK", "BRPT.JK", "SRTG.JK", "MTLA.JK",
    "MAPI.JK", "MAPA.JK", "AMRT.JK", "ACES.JK", "FILM.JK", "MDKA.JK", "MBMA.JK", "AMMN.JK", "NCKL.JK", "NICL.JK",

    # SAHAM TRENDING + GORENGAN LAIN
    "KOTA.JK", "MINA.JK", "ASPR.JK", "BCIP.JK", "PADI.JK", "BUVA.JK", "PIPA.JK", "LABA.JK", "SUNI.JK", "TRON.JK",
    "VKTR.JK", "WIFI.JK", "RAJA.JK", "GULA.JK", "SMIL.JK", "KJEN.JK", "ATLA.JK", "CBRE.JK", "BULL.JK", "KRYA.JK",
    "KREN.JK", "WINS.JK", "SGER.JK", "TELE.JK", "TGRA.JK", "CARE.JK", "ERAA.JK", "WIRG.JK", "BIPI.JK", "MIRA.JK"
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

def analisa_saham(ticker, mode="praara"):
    try:
        saham = yf.Ticker(ticker)
        df = saham.history(period="3mo")
        if df.empty or len(df) < 30:
            return None

        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = hitung_rsi(df['Close'])
        macd, signal, hist = hitung_macd(df['Close'])
        df['MACD'] = macd
        df['Signal'] = signal
        df['BB_Upper'] = df['Close'].rolling(window=20).mean() + df['Close'].rolling(window=20).std() * 2
        df['BB_Lower'] = df['Close'].rolling(window=20).mean() - df['Close'].rolling(window=20).std() * 2

        harga = df['Close'].iloc[-1]
        ma5 = df['MA5'].iloc[-1]
        ma20 = df['MA20'].iloc[-1]
        ma50 = df['MA50'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        macd_val = df['MACD'].iloc[-1]
        signal_val = df['Signal'].iloc[-1]
        vol = df['Volume'].iloc[-1]
        avg_vol = df['Volume'].rolling(window=20).mean().iloc[-1]
        bb_upper = df['BB_Upper'].iloc[-1]
        bb_lower = df['BB_Lower'].iloc[-1]
        harga_kemarin = df['Close'].iloc[-2]
        vol_kemarin = df['Volume'].iloc[-2]

        skor = 0
        alasan = []

        # 1. PRAARA - All Round AKUMULASI SEHAT
        if mode == "praara":
            if harga > ma20 > ma50: skor += 2; alasan.append("Uptrend MA20>MA50")
            if rsi < 30: skor += 2; alasan.append("RSI Oversold")
            elif rsi > 50 and rsi < 70: skor += 1; alasan.append("RSI Kuat")
            if macd_val > signal_val: skor += 2; alasan.append("MACD Bullish")
            if vol > avg_vol * 1.5: skor += 1; alasan.append("Volume Meledak")
            batas_skor = 4

        # 2. SWING - MA20 + RSI 45-65
        elif mode == "swing":
            if harga > ma20: skor += 2; alasan.append("Harga > MA20")
            if rsi > 45 and rsi < 65: skor += 2; alasan.append("RSI Swing 45-65")
            if vol > avg_vol * 1.2: skor += 1; alasan.append("Volume Oke")
            if macd_val > signal_val: skor += 1; alasan.append("MACD Bullish")
            batas_skor = 3

        # 3. DAYTRADE - Momentum Intraday
        elif mode == "daytrade":
            if harga > harga_kemarin * 1.01: skor += 2; alasan.append("Naik >1% Hari Ini")
            if vol > vol_kemarin * 1.5: skor += 2; alasan.append("Volume Naik 50%")
            if rsi > 55 and rsi < 85: skor += 1; alasan.append("RSI Momentum")
            if harga > ma5: skor += 1; alasan.append("Harga > MA5")
            batas_skor = 3

        # 4. SCALPING - BB Squeeze + Volume
        elif mode == "scalping":
            bb_width = (bb_upper - bb_lower) / df['MA20'].iloc[-1]
            if bb_width < 0.05: skor += 1; alasan.append("BB Squeeze")
            if harga > bb_upper: skor += 2; alasan.append("Breakout BB Atas")
            if vol > avg_vol * 2: skor += 2; alasan.append("Volume 2x Rata2")
            if rsi > 60: skor += 1; alasan.append("RSI Kuat")
            batas_skor = 3

        # 5. BPJS - Bandar Pelan-pelan Jajan Saham = AKUMULASI SEPI
        elif mode == "bpjs":
            if harga > ma20 > ma50: skor += 1; alasan.append("Uptrend Sehat")
            if rsi > 40 and rsi < 60: skor += 2; alasan.append("RSI Netral Akumulasi")
            if vol < avg_vol * 0.8 and harga > harga_kemarin: skor += 2; alasan.append("Harga Naik Vol Kering")
            if macd_val > signal_val: skor += 1; alasan.append("MACD Bullish Diam2")
            batas_skor = 3

        # 6. TREND - Gabungan Daytrade + Scalping buat saham terbang
        elif mode == "trend":
            if harga > harga_kemarin * 1.03: skor += 3; alasan.append("Naik >3% GILA")
            elif harga > harga_kemarin * 1.01: skor += 2; alasan.append("Naik >1% Hari Ini")
            if vol > avg_vol * 2: skor += 2; alasan.append("Volume 2x Rata2")
            if harga > bb_upper: skor += 2; alasan.append("Jebol BB Upper")
            if rsi > 70: skor += 1; alasan.append("RSI Overbought Parah")
            batas_skor = 4

        if skor >= batas_skor:
            return {
                "ticker": ticker.replace(".JK", ""),
                "harga": harga,
                "skor": skor,
                "alasan": ", ".join(alasan),
                "rsi": round(rsi, 1),
                "perubahan": round((harga/harga_kemarin-1)*100, 2)
            }
        return None
    except:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Bot Dewa IDX v1.3.3 Konglo Aktif!\n\n"
        "Command Screener 150 Saham:\n"
        "/praara - Akumulasi Sehat\n"
        "/swing - Swing MA20 + RSI\n"
        "/bpjs - Bandar Jajan Sepi\n"
        "/daytrade - Momentum Intraday\n"
        "/scalping - Breakout BB + Volume\n"
        "/trend - SAHAM LAGI TERBANG\n\n"
        "Command Analisa:\n"
        "/harga KODE - Cek harga, contoh: /harga BBCA\n"
        "/sinyal KODE - Analisa momentum 1 saham"
    )

async def screener_generic(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str, judul: str):
    await update.message.reply_text(f"🚀 Screening {judul} 150 saham... Sabar 45-90 detik bro...")
    hasil_sinyal = []
    for ticker in SAHAM_UNGGULAN:
        res = analisa_saham(ticker, mode)
        if res:
            hasil_sinyal.append(res)

    if not hasil_sinyal:
        await update.message.reply_text(f"Zonk bro 😭 Nggak ada saham lolos {judul} hari ini.")
        return

    hasil_sinyal = sorted(hasil_sinyal, key=lambda x: x['skor'], reverse=True)[:5]
    teks = f"🔥 TOP 5 {judul.upper()} 🔥\n\n"
    for i, s in enumerate(hasil_sinyal, 1):
        teks += f"{i}. {s['ticker']} - Rp {s['harga']:,.0f} ({s['perubahan']}%)\n Skor: {s['skor']} | RSI: {s['rsi']}\n {s['alasan']}\n\n"
    teks += "Disclaimer: Bukan ajakan beli. DYOR!"
    await update.message.reply_text(teks)

async def praara(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await screener_generic(update, context, "praara", "Akumulasi Sehat")

async def swing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await screener_generic(update, context, "swing", "Swing MA20+RSI")

async def daytrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await screener_generic(update, context, "daytrade", "Daytrade Momentum")

async def scalping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await screener_generic(update, context, "scalping", "Scalping Breakout")

async def bpjs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await screener_generic(update, context, "bpjs", "BPJS - Bandar Jajan")

async def trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await screener_generic(update, context, "trend", "Saham Lagi Terbang")

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
    # GANTI KE DAYTRADE BIAR PTRO BRPT KEBACA
    hasil = analisa_saham(kode, "daytrade")
    if hasil:
        teks = f"📈 SINYAL {hasil['ticker']}\nHarga: Rp {hasil['harga']:,.0f} ({hasil['perubahan']}%)\nSkor: {hasil['skor']}\nRSI: {hasil['rsi']}\nAlasan: {hasil['alasan']}"
    else:
        teks = f"Nggak ada sinyal momentum buat {kode.replace('.JK','')} sekarang. Coba /trend atau /praara"
    await update.message.reply_text(teks)

if __name__ == '__main__':
    print("Bot Dewa IDX v1.3.3 Konglo jalan...")
    app = ApplicationBuilder().token(TOKEN_BOT).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("harga", harga))
    app.add_handler(CommandHandler("sinyal", sinyal))
    app.add_handler(CommandHandler("praara", praara))
    app.add_handler(CommandHandler("swing", swing))
    app.add_handler(CommandHandler("daytrade", daytrade))
    app.add_handler(CommandHandler("scalping", scalping))
    app.add_handler(CommandHandler("bpjs", bpjs))
    app.add_handler(CommandHandler("trend", trend))

    app.run_polling()
