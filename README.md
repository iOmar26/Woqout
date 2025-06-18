# Woqout 

 "Woqout" is a Flask web application that calculates:
- Parts of the night and the beginnig and end time of each one (third,sixth...etc). which is needed for some acts of worship in Islam especially Maliki school.
- The six time parts of Jumaa prayer that prophet upon him be peace mentioned according to Maliki school.

## 🌍 How it works
- User selects a country and city
- App calls the AlAdhan API to fetch timing data
- Segments of the night and Jumua hours are calculated locally

## 🚀 Run it locally
```bash
pip install -r requirements.txt
python app.py

