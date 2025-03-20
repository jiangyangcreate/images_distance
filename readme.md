## 准备

把python312.dll放到exe同级目录下
## 打包命令

pyinstaller --add-data "index_demo.html;." --add-binary "python312.dll;." --icon "my.ico" --noconsole main.py


## 查看exe

```
dist/main.exe
```

