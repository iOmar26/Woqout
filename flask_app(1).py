from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

def time_to_hours_minutes(t):
    h, m = map(int, t.split(":"))
    return h, m

def format_time_12_str(t):
    dt = datetime.strptime(t, "%H:%M")
    return dt.strftime("%I:%M %p")

def format_time(total_seconds):
    total_seconds = total_seconds % (24 * 3600)
    total_minutes = round(total_seconds / 60)
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    period = "AM" if hours < 12 else "PM"
    h12 = hours % 12
    if h12 == 0:
        h12 = 12
    return f"{h12:02d}:{minutes:02d} {period}"

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    today = datetime.today()
    city = request.form.get("city") if request.method == "POST" else "Hofuf"
    country = request.form.get("country") if request.method == "POST" else "Saudi Arabia"

    api_url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=4"
    response = requests.get(api_url)
    data = response.json()
    output = ""

    if data["code"] == 200:
        timings = data["data"]["timings"]
        t_imsak   = timings["Imsak"]
        t_sobh    = timings["Fajr"]
        t_shurooq = timings["Sunrise"]
        t_zuhr    = timings["Dhuhr"]
        t_maghrib = timings["Maghrib"]
        t_asr     = timings["Asr"]
        t_isha    = timings["Isha"]

        output += f"الفجر: {format_time_12_str(t_sobh)}\n"
        output += f"الشروق: {format_time_12_str(t_shurooq)}\n"
        output += f"الظهر: {format_time_12_str(t_zuhr)}\n"
        output += f"العصر: {format_time_12_str(t_asr)}\n"
        output += f"المغرب: {format_time_12_str(t_maghrib)}\n"
        output += f"العشاء: {format_time_12_str(t_isha)}\n\n"

        h_imsak, m_imsak     = time_to_hours_minutes(t_imsak)
        h_sobh,  m_sobh      = time_to_hours_minutes(t_sobh)
        h_zuhr,  m_zuhr      = time_to_hours_minutes(t_zuhr)
        h_maghrib, m_maghrib = time_to_hours_minutes(t_maghrib)

        total1 = (h_maghrib * 3600) + (m_maghrib * 60)
        total2 = (h_sobh    * 3600) + (m_sobh    * 60)
        total3 = (h_imsak   * 3600) + (m_imsak   * 60)

        if total2 <= total1:
            total2 += 24 * 3600
        if total3 <= total1:
            total3 += 24 * 3600

        Night  = total2  - total1
        Night2 = total3  - total1
        Sixth  = Night   // 6
        Sixth2 = Night2  // 6

        fthird = total1 + Sixth2 * 2
        lthird = total1 + Sixth  * 4
        lsixth = total1 + Sixth  * 5

        output += f"نهاية الثلث الأول: {format_time(fthird)}\n"
        output += f"بداية الثلث الأخير: {format_time(lthird)}\n"
        output += f"بداية السدس الأخير: {format_time(lsixth)}\n\n"

        days_until_friday = (4 - today.weekday()) % 7
        next_friday = today if days_until_friday == 0 else today + timedelta(days=days_until_friday)
        date_str    = next_friday.strftime("%d-%m-%Y")
        friday_url  = f"http://api.aladhan.com/v1/timingsByCity/{date_str}?city={city}&country={country}&method=4"
        fr_resp     = requests.get(friday_url)
        fr_data     = fr_resp.json()

        if fr_data["code"] == 200:
            fr_timings = fr_data["data"]["timings"]
            t_sobh_fr  = fr_timings["Fajr"]
            t_zuhr_fr  = fr_timings["Dhuhr"]
            h_sobh, m_sobh = time_to_hours_minutes(t_sobh_fr)
            h_zuhr, m_zuhr = time_to_hours_minutes(t_zuhr_fr)

            total1_sec = (h_sobh * 3600) + (m_sobh * 60)
            total2_sec = (h_zuhr * 3600) + (m_zuhr * 60)
        else:
            error = "⚠️ حدث خطأ في جلب بيانات الجمعة القادمة."
            return render_template('index.html', output="", error=error)

        Nahar_sec = total2_sec - total1_sec
        shb_sec   = Nahar_sec / 6
        SxH_sec   = total2_sec - shb_sec
        shp_sec   = shb_sec   / 5

        hour_names = [
            "الأولى<br>(كأنما قرب بدنة)",
            "الثانية<br>(كأنما قرب بقرة)",
            "الثالثة<br>(كأنما قرب كبشًا أقرن)",
            "الرابعة<br>(كأنما قرب دجاجة)",
            "الخامسة<br>(كأنما قرب بيضة)"
        ]

        title = "حساب ساعات الجمعة" if days_until_friday == 0 else "حساب ساعات الجمعة القادمة"
        output += f"{title}:\n"
        for i in range(5):
            start_i = format_time(SxH_sec + shp_sec * i)
            output += f"بداية الساعة {hour_names[i]}: {start_i}\n"

        return render_template('index.html', output=output, error=None)

    else:
        error = "⚠️ الدولة أو المدينة غير صحيحة. حاول مرة أخرى."
        return render_template('index.html', output="", error=error)

