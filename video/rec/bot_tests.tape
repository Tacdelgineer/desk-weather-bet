Output video/work/rec/vhs_bot_tests.mp4
Set Shell "bash"
Set FontSize 30
Set Width 1920
Set Height 1080
Set Framerate 30
Set Padding 40
Set Theme "Builtin Dark"
Set TypingSpeed 45ms
Hide
Type "export PS1='$ ' HISTFILE=/dev/null; cd ~/Projects/desk-weather-bet; clear" Enter
Sleep 500ms
Show
Type "uv run pytest tests/test_live.py -v 2>&1 | grep -v /home/ | tail -40"
Enter
Wait+Screen@120s /passed/
Sleep 3s
Type "clear; python3 -m json.tool logs/live/2026-10-24_picks.json | grep -E 'mode|ticker|side|price|edge|p_bet' | head -16"
Enter
Sleep 6s
