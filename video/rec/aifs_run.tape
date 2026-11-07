Output video/work/rec/vhs_aifs_run.mp4
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
Type "uv run --project model/aifs python model/run_aifs.py --date 2026-11-06T06 --lead 60 2>&1 | grep --line-buffered -v -e /home/ -e warn -e 'return torch' -e nstall"
Sleep 600ms
Enter
Wait+Screen@300s /saved/
Sleep 3s
