import csv
from selenium import webdriver
#from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#variables for configuration
accountsFilePath = "Accounts.csv" #Put the full file path
chromeHeadless = False #Set to True to make chrome not visible
accIdToSkipList = [] #Use the ID of the Account you want to skip Eg [1, 3, 7]

class D2rAccount:
    def __init__(self, id_val, Acct, AccountLabel, Batches, TimeActive, CustomLaunchArguments, AuthenticationMethod, PW, Token, WindowXCoordinates, WindowYCoordinates, WindowHeight, WindowWidth):
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

def Read_Accounts_From_CSV(filename):
    account_list = []
    with open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
        # Use DictReader for easy access by column name (header)
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Instantiate the class using data from each row dictionary
            account = D2rAccount(
                id_val = row['ID'],
                Acct = row['Acct'],
                AccountLabel = row['AccountLabel'],
                Batches = row['Batches'],
                TimeActive = row['TimeActive'],
                CustomLaunchArguments = row['CustomLaunchArguments'],
                AuthenticationMethod = row['AuthenticationMethod'],
                PW = row['PW'],
                Token = row['Token'],
                WindowXCoordinates = row.get('WindowXCoordinates', None),
                WindowYCoordinates = row.get('WindowYCoordinates', None),
                WindowHeight = row.get('WindowHeight', None),
                WindowWidth = row.get('WindowWidth', None)
            )
            account_list.append(account)
    return account_list

def trim_token(token):
    token = token.split('=')
    trimed_token = token[1].split('&')
    return trimed_token[0]

def Write_Accounts_To_CSV(accounts, filename):
    data_to_write = [acc.__dict__ for acc in accounts]
    fieldnames = ['ID', 'Acct', 'AccountLabel', 'Batches', 'TimeActive', 'CustomLaunchArguments', 'AuthenticationMethod', 'PW', 'Token', 'WindowXCoordinates','WindowYCoordinates' , 'WindowHeight', 'WindowWidth']
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()  # Write the header row
        writer.writerows(data_to_write)  # Write all data rows
def Get_Token(account, password):
    try:
        options = Options()
        if chromeHeadless:
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
        return trim_token(token)
    except:
        return 1


if __name__ == '__main__':
    all_accounts = Read_Accounts_From_CSV(accountsFilePath)
    for acc in all_accounts:
        if acc.ID not in accIdToSkipList:
            print(f"Working on Account: {acc.ID}  {acc.AccountLabel}   {acc.Acct}")
            newToken = Get_Token(acc.Acct, acc.PW)
            if not newToken == 1:
                acc.Token = newToken
                print(f"Done with Account:  {acc.ID}  {acc.AccountLabel}   {acc.Acct}")
                #print(acc.Token) #prints new token
            else:
                print("Failed to login. Moving on to next account.")
        else:
            print(f"Skipping Account:   {acc.ID}  {acc.AccountLabel}   {acc.Acct}")

    Write_Accounts_To_CSV(all_accounts, accountsFilePath)
    print("New Accounts.csv finished.")