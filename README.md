# A tool for reservating seat in Wuhan University.

> author: hazzel

> Yes! the author is me. I did it! :))

If you miss the opportunity to reserve seats on time again and again, why not try this.

<del>The project contains TWO BRANCHES. One is for single person, while the other is for couples.</del>
(Because of some reasons, I will only provide SINGLE version, which is enough for you to take seats.)

__If you are not farmiliar with scripts or environment building, you can run .exe in ./bin V*/ dict. after edit your information in /bin V*/user.txt__



## Version for single person

In the dictonary, you can find such two files - `main-single.py` and `user.txt` - the former of which is the entry, while the other is the config file.

## Version for couples

To be added.

### How to run it

If you want to run the script, you should build suitable environment.

### What you need is:
* PIL: the Python Image Library for handle pictures
* tesseract-ocr: The OCR engine
* pytesseract: the library for Python to call tesseract
* requests: make request
* bs4: beautiful-soup to manage content on HTML page

### Ubuntu X64 (tested on Ubuntu 14.04 x64)

```
# Prepare
git clone https://github.com/h4zze1/WHULibSeat.git
git checkout single
sudo apt update
sudo apt install python-pil
sudo apt install tesseract-ocr

sudo pip install pytesseract
sudo pip install requests
sudo pip install bs4

# Run
# ! Modify the information in user.txt
python main-single.py
# ! Follow the intruction in interface
# ! Just wait 

```

### Windows (tested on Win10)

Install PIL(Python Image Lib):

[ Win x64 Click Here ](https://github.com/lightkeeper/lswindows-lib/blob/master/amd64/python/PIL-1.1.7.win-amd64-py2.7.exe?raw=true)

[ Win x32 Click Here ](http://effbot.org/downloads/PIL-1.1.7.win32-py2.7.exe)

Install tesseract-ocr engine

[ tesseract-ocr Click Here ](http://code.google.com/p/tesseract-ocr)

```
# Prepare
# ! Install PIL
# ! Install tesseract 
git clone https://github.com/h4zze1/WHULibSeat.git
git checkout single
sudo pip install pytesseract
sudo pip install requests
sudo pip install bs4

# Run
# ! Modify the information in user.txt
python main-single.py
# ! Follow the intruction in interface
# ! Just wait 
```

## Mac

```
Mac is too expensive for me to afford.
```

Details have been posted on my personal blog. http://www.hazzel.cn/archives/53.html

or you can visit >> [Online Version](http://seat.lib.hazzel.cn) << after you ask me for Inviting Code.

PS: If you have any questions, do not hesitate to contact me. I am willing to solve your problems.

I am still working to perfect this script for your need.

