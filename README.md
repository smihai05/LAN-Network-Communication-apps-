# LAN Network communication apps from PC A to PC B 
Two applications that allow you to communicate over your local internet network: “Parrot” (should be on PC A) which is used as the server to send messages and change the IP of the receiver and “Pirate” (should be on PC B) which is used as the receiver to read the messages that are send in the LAN network 

After the files are on your computers simply run this command : 

py -m PyInstaller --clean --onefile --windowed --noconsole  --icon="parrot.ico" parrot.py

py -m PyInstaller --clean --onefile --windowed --noconsole  --icon="pirate.ico" pirate.py
