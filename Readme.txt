I created this to be used with Shupershuff's D2RLoader https://github.com/shupershuff/Diablo2RLoader.
This is a very rough python script I don’t really program too often anymore.  Feel free to use any part of it in your own scripts.  I’m not sure how to package it all up so you will need to install a python IDE and install the python packages. For it to work you can NOT use ConvertPlainTextSecrets in D2RLoader.  I can’t unencrypt them, like its supposed to be.  It does support RememberWindowLocations. If you do not have RememberWindowLocations enabled the script will add the colums to your Accounts.csv.  You can configure the accIdToSkipList variable to add the accounts you want to skip, useful if you have old tokens that haven’t expired.

prerequisites
setup a python IDE
pip install selenium
you will also need to have the latest google chrome browser.

How it works
It uses the Accounts.csv for the username and passwords to login to each account then one at a time and grab the new token.  It uses selenium to automate the login of each account in google chrome. It opens up a new incognito window.  Logins in through both the account name page and password page and grabs the new Token URL.
It goes through all accounts then saves the new Accounts.csv. Once done just load up d2rloader with the new Accounts.csv.  The more accounts you have the longer it takes.


Future Goals
Check if dependencies are met.
The ability to pass .Json string as an argument with PowerShell. So maybe D2RLauncher can send a .json string or just a csv string of the accounts that need new tokens  and return the tokens. That way the user passwords and tokens can be stored securely.

