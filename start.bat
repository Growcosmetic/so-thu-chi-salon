@echo off
echo Dang khoi dong ung dung So Thu Chi Salon...
cd /d %~dp0
python -m streamlit run app.py
pause

