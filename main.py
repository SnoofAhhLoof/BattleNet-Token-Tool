import csv
import sys
import io
import os
from io import StringIO
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#variables for configuration
accountsFilePath = "Accounts.csv" #Put the full file path
chromeHeadless = False #Set to True to make chrome not visible
accIdToSkipList = [] #Use the ID of the Account you want to skip Eg [1, 3, 7]
currentDirectory = os.path.dirname(os.path.abspath(__file__))
currentFilePath = os.path.join(currentDirectory, 'Accounts.csv')
all_accounts = []

def Check_Google_Chrome():
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getlogin())
    ]
    for path in paths:
        if os.path.exists(path):
            return True
    messagebox.showwarning('Did Not Detect Google Chrome', 'The Automated Login will not work without Google Chrome. Please download and install Google Chrome, then run this.')
    return False

class D2rAccount:
    def __init__(self, id_val, Acct=None, AccountLabel=None, Batches=None, TimeActive=None, CustomLaunchArguments=None, AuthenticationMethod=None, PW=None, Token=None, WindowXCoordinates=None, WindowYCoordinates=None, WindowHeight=None, WindowWidth=None):
        # Convert types from string (csv default) to appropriate types
        self.ID = int(id_val)
        self.Acct = Acct
        self.AccountLabel = AccountLabel
        self.Batches = Batches
        self.TimeActive = TimeActive
        self.CustomLaunchArguments = CustomLaunchArguments
        self.AuthenticationMethod = AuthenticationMethod
        self.PW = PW
        self.Token = Token
        self.WindowXCoordinates = WindowXCoordinates
        self.WindowYCoordinates = WindowYCoordinates
        self.WindowHeight = WindowHeight
        self.WindowWidth = WindowWidth

    def String_Vars(self):
        return {
            'ID': str(self.ID),
            'Acct': self.Acct,
            'PW': self.PW,
            'Token': self.Token
        }


def Read_Accounts_From_CSV(csvInput, isString=False):
    account_list = []
    if isString:
        csvString = StringIO(csvInput, newline='')
        reader = csv.DictReader(csvString, delimiter=',')
        for row in reader:
            try:
                account = D2rAccount(
                    id_val=int(row['ID']),
                    Acct=row['Acct'],
                    PW=row['PW'],
                    Token=row['Token']
                    )
                account_list.append(account)
            except ValueError:
                print("Ran into error reading the CSV")
        return account_list

    else:
        with open(csvInput, mode='r', newline='', encoding='utf-8') as csvfile:
            # Use DictReader for easy access by column name (header)
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Instantiate the class using data from each row dictionary
                account = D2rAccount(
                    id_val=row['ID'],
                    Acct=row['Acct'],
                    AccountLabel=row['AccountLabel'],
                    Batches=row['Batches'],
                    TimeActive=row['TimeActive'],
                    CustomLaunchArguments=row['CustomLaunchArguments'],
                    AuthenticationMethod=row['AuthenticationMethod'],
                    PW=row['PW'],
                    Token=row['Token'],
                    WindowXCoordinates=row.get('WindowXCoordinates', None),
                    WindowYCoordinates=row.get('WindowYCoordinates', None),
                    WindowHeight=row.get('WindowHeight', None),
                    WindowWidth=row.get('WindowWidth', None)
                )
                account_list.append(account)
        return account_list

#Two seperate functions
#Write_Accounts_CSV_File
#Write_Accounts_CSV_String

def Write_Accounts_CSV_File(accounts, filePath):
    data_to_write = [acc.__dict__ for acc in accounts]
    fieldnames = ['ID', 'Acct', 'AccountLabel', 'Batches', 'TimeActive', 'CustomLaunchArguments',
                  'AuthenticationMethod', 'PW', 'Token', 'WindowXCoordinates', 'WindowYCoordinates', 'WindowHeight',
                  'WindowWidth']
    with open(filePath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()  # Write the header row
        writer.writerows(data_to_write)  # Write all data rows

def Write_Accounts_CSV_String(accounts):
    data = [acc.String_Vars() for acc in accounts]
    fieldnames = ['ID', 'Acct', 'PW', 'Token']
    with io.StringIO(newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        csv_string = csvfile.getvalue()
    return csv_string

def Get_Token(account, password, headless=True):
    try:
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--incognito")  # find this helps to make sure the account doesn't stay logged in for next session
        browser = webdriver.Chrome(options=options)

        browser.get('https://us.battle.net/login/en/?externalChallenge=login&app=OSI')
        browser.find_element(By.ID, 'accountName').send_keys(account)
        browser.find_element(By.CSS_SELECTOR, '#submit').click()

        WebDriverWait(browser, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#password')))  # wait for password screen
        browser.find_element(By.ID, 'password').send_keys(password)
        old_url = browser.current_url
        browser.find_element(By.CSS_SELECTOR, '#submit').click()
        WebDriverWait(browser, 5).until(EC.url_changes(old_url))

        token = browser.current_url
        browser.quit()
        token = token.split('=')
        trimedToken = token[1].split('&')
        return trimedToken[0]
    except:
        return 1

if __name__ == "__main__":
    Check_Google_Chrome()
    # Check if at least one argument (besides the script name) is provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "--CSV":
            all_accounts = Read_Accounts_From_CSV(sys.argv[2], True)
            for acc in all_accounts:
                newToken = Get_Token(acc.Acct, acc.PW, True)
                if not newToken == 1:
                    acc.Token = newToken
            returnCsv = Write_Accounts_CSV_String(all_accounts)
            print(returnCsv)
        elif sys.argv[1] == "--All-Accounts":
            if len(sys.argv) < 1:
                if os.path.exists(sys.argv[2]):
                    currentFilePath = sys.argv[2]
                else:
                    messagebox.showwarning(f'Not a file path:  {sys.argv[2]}')
                    sys.exit()
            else:
                if not os.path.exists(currentFilePath):
                    messagebox.showwarning(f'Default path doesnt exist:  {currentFilePath}')
                    sys.exit()
            all_accounts = Read_Accounts_From_CSV(currentFilePath)
            for acc in all_accounts:
                newToken = Get_Token(acc.Acct, acc.PW, False)
                if newToken == 1:
                    messagebox.showwarning(f'{acc.ID} , {acc.AccountLabel}: Failed to login')
                else:
                    acc.Token = newToken
            Write_Accounts_CSV_File(all_accounts, currentFilePath)
        elif sys.argv[1] == "--All-Accounts-Headless":
            if len(sys.argv) < 1:
                if os.path.exists(sys.argv[2]):
                    currentFilePath = sys.argv[2]
                else:
                    messagebox.showwarning(f'Not a file path:  {sys.argv[2]}')
                    sys.exit()
            else:
                if not os.path.exists(currentFilePath):
                    messagebox.showwarning(f'Default path doesnt exist:  {currentFilePath}')
                    sys.exit()
            all_accounts = Read_Accounts_From_CSV(currentFilePath)
            for acc in all_accounts:
                newToken = Get_Token(acc.Acct, acc.PW)
                if newToken == 1:
                    messagebox.showwarning(f'{acc.ID} , {acc.AccountLabel}: Failed to login')
                else:
                    acc.Token = newToken
            Write_Accounts_CSV_File(all_accounts, currentFilePath)
        else:
            print("Arguments provided not supported.")
    else:
        all_accounts = Read_Accounts_From_CSV(accountsFilePath)
        for acc in all_accounts:
            if acc.ID not in accIdToSkipList:
                print(f"Working on Account: {acc.ID}  {acc.AccountLabel}   {acc.Acct}")
                newToken = Get_Token(acc.Acct, acc.PW)
                if not newToken == 1:
                    acc.Token = newToken
                    print(f"Done with Account:  {acc.ID}  {acc.AccountLabel}   {acc.Acct}")
                    # print(acc.Token) #prints new token
                else:
                    print("Failed to login. Moving on to next account.")
            else:
                print(f"Skipping Account:   {acc.ID}  {acc.AccountLabel}   {acc.Acct}")
        Write_Accounts_CSV_File(all_accounts, accountsFilePath)
        print("New Accounts.csv finished.")
    sys.exit()