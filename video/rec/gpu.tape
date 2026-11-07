Output video/work/rec/vhs_gpu.mp4
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
Type "nvidia-smi --query-gpu=name,memory.total --format=csv"
Enter
Sleep 2s
Type "nvidia-smi --query-gpu=name,driver_version,temperature.gpu,utilization.gpu,clocks.sm --format=csv"
Enter
Sleep 4s
