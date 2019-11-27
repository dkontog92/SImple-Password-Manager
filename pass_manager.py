from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import json, base64, time, os
import pandas as pd
import getpass
from tabulate import _table_formats, tabulate


def gen_key(passwrd):
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(passwrd)
    return base64.urlsafe_b64encode(digest.finalize())

def check_file(filename):
    
    if os.path.exists(filename):
        #user_pass = input('Enter decryption password: ').encode()
        user_pass = getpass.getpass(prompt = 'Enter decryption password: ').encode()
    else:
        print('File not found. Creating new file.')
        f=open(filename,'x')
        f.close()
        user_pass = input('Enter encryption password: ').encode()
    
    key = gen_key(user_pass)
    fernet = Fernet(key)
    
    reader = open(filename, 'rb')
    content = reader.read()
    reader.close()
    if len(content) > 1:
        try:
            decrypted_content = fernet.decrypt(content)
            print('Successful entry')            
            content = json.loads(decrypted_content)
            time.sleep(0.5)
            print('Entering Password Manager')
            #return content, fernet, True
            return fernet, True        
        except:
            time.sleep(0.5)
            print('Authentication Failed!')
            time.sleep(0.5)
            print('Exiting Password Manager...\n')
            time.sleep(0.2)
            #return -1, -1, False
            return -1, False
    else:
        #return {}, fernet, True
        return fernet, True

def read_file(fernet, filename):
    
    reader = open(filename, 'rb')
    content = reader.read()
    reader.close()
    if len(content) > 0:
        decrypted_content = fernet.decrypt(content)    
        content = json.loads(decrypted_content)
        return content
    else:
        return {}

def update_file(passwords, fernet, filename):
    
    if passwords:
        passwords_jsonized = json.dumps(passwords)        
        new_encr_passwords = fernet.encrypt(passwords_jsonized.encode())    
        
        reader = open(filename, 'wb')    
        reader.write(new_encr_passwords)
        reader.close()
    else:
        open(filename, 'wb').close()


def store_pass(fernet, filename, passwords):
   
    site = input('Site/App: ')
    
    if site in passwords.keys():
        input_replace = input('Password for this site already exists. Replace? (y/n): ')
        if input_replace == 'n':
            print('Keeping stored password.')
        elif input_replace == 'y': 
            userid = input('Userid: ')
            pasword = input('Password: ')
            other = input('Other details: ') 
            passwords[site] = {'User ID': userid, 'Password':  pasword, 'Other Details': other}
            update_file(passwords, fernet, filename)    
        else:
            print('Wrong input.')
    else:
        userid = input('Userid: ')
        pasword = input('Password: ')
        other = input('Other details: ')
        passwords[site] = {'User ID': userid, 'Password':  pasword, 'Other Details': other}
        update_file(passwords, fernet, filename)  

def change_password(passwords, filename):
    
    user_pass = input('Enter new decryption password: ').encode()
    key = gen_key(user_pass)
    fernet = Fernet(key)
    
    passwords_jsonized = json.dumps(passwords)        
    new_encr_passwords = fernet.encrypt(passwords_jsonized.encode())    
    
    reader = open(filename, 'wb')    
    reader.write(new_encr_passwords)
    reader.close()
    time.sleep(0.5)
    print('\nEncryption code changed')
    time.sleep(0.5)
    return fernet

def print_passwords(passwords):
    if len(passwords) > 0:
        df = pd.DataFrame(passwords).transpose()
        df['Site'] = df.index
        df = df[['Site','User ID', 'Password', 'Other Details']]
        df = df.reset_index(drop = True) 
        #pd.options.display.width=None
        #pd.set_option("display.max_rows", len(df))
        
        #format_list = list(_table_formats.keys())
        #for f in format_list:
        #print("\nformat: {}\n".format(f))
        print('\n')
        print('-'*153)
        print('-'*47 +' '*20 + 'PASSWORDS DATABASE' +' '*21 +  '-'*47)
        print('-'*153)
        print('\n')
        print(tabulate(df, headers = df.columns, tablefmt='fancy_grid', numalign='center'))
        print('-'*160)
        print('\n')
        #pd.reset_option('display.max_rows')
        input("Press Enter to continue...")
    else:
        print('No passwords stored')
    
    #print('\n\n')
    #print(tabulate(df, headers = df.columns))
    
    
    
    
def remove_password(passwords, f, filename):
    web = input('Choose website to delete password: ')
    if web in passwords.keys():
        del passwords[web]
        update_file(passwords,f,filename)
    else:
        time.sleep(0.5)
        print('\nPASSWORD NOT FOUND.')
        time.sleep(0.5)


def load_passwords(f,filename,file_excel):
    
    passwords = pd.read_excel('passwords_store.xlsx')
    pass_dict = {str(key): {} for key in passwords['Site']}

    for key in pass_dict.keys():
        data = passwords.loc[passwords['Site']==key,passwords.columns[1:]].reset_index()
        
        pass_dict[key] = {'User ID': str(data['UserID'][0]), 'Password':  str(data['Password'][0]), 'Other Details': str(data['Other'][0])}
    
    update_file(pass_dict, f, filename)
        

def load_passwords2(f,passwords_old,filename,file_excel):
    
    
    passwords = pd.read_excel('passwords_store.xlsx')
    pass_dict = {str(key): {} for key in passwords['Site']}

    for key in pass_dict.keys():
        data = passwords.loc[passwords['Site']==key,passwords.columns[1:]].reset_index()
        
        pass_dict[key] = {'User ID': str(data['UserID'][0]), 'Password':  str(data['Password'][0]), 'Other Details': str(data['Other'][0])}

    user_input = input('Replace or append (r/a): ')
    
    if user_input == 'r':
        update_file(pass_dict, f, filename)
    elif user_input == 'a':
        new_passwords = dict(passwords_old.items() + pass_dict.items())
        update_file(new_passwords, f, filename)
    else:
        print('Wrong input')

 

def search_pass(passwords):
    df = pd.DataFrame(passwords)#.transpose()
    search = input('Enter the site: ')
    
    matches = []
    for col in list(df.columns):
        if search.lower() in col.lower():
            matches.append(col)
        else:
            pass
    
    if matches:
        df = pd.DataFrame(df[matches]).transpose()
        df = df[['User ID', 'Password', 'Other Details']]
        pd.set_option("display.max_rows", len(df))
        #df.style.set_properties({'text-align': 'center'})
        print('\n')
        print('-'*80)
        print('-'*20 +' '*13 + 'SEARCH RESULTS' +' '*13 +  '-'*20)
        print('-'*80)
        print(df)    
    else:
        print('\n No results found.')
               
    
def main_menu():
    time.sleep(0.2)
    print('\n')
    print('ENTER YOUR CHOICE FROM THE OPTIONS BELOW \n')
    print('\t"1": PRINT stored passwords')
    print('\t"2": SEARCH password by site')    
    print('\t"3": STORE a new password (or ALTER existing password)')
    print('\t"4": DELETE an existing password')
    print('\t"5": CHANGE the encryption code')
    print('\t"6": LOAD passwords from external excel file')    
    print('\t"0": EXIT to Desktop') 


def get_input(f, filename):
    
    flag = True
    fernet = f
    passwords = read_file(fernet, filename)
    option = input('>: ')
    if option == '1':
        if len(passwords) > 0:
            print_passwords(passwords)
        else:
            print('\nNo passwords stored.')
    elif option == '2':
        search_pass(passwords)       
    elif option == '3':
        store_pass(fernet, filename, passwords)
    elif option == '4':
        remove_password(passwords, fernet, filename)
    elif option == '5':
        fernet = change_password(passwords, filename)
    elif option == '6':
        load_passwords2(fernet, passwords, filename, 'passwords_store.xlsx')
    elif option == '0':
        flag = False
    else:
        print('Wrong input, try again.')
    
    return flag, fernet
    
     
def main():
    print('\n')
    print('-'*80)
    print('-'*20 +' '*10 + 'PASSWORD MANAGER v.1' +' '*10 +  '-'*20)
    print('-'*80)
    
    filename = 'passwords.txt'
    
    f, flag = check_file(filename)
    
    while(flag):
        main_menu()
        flag, f = get_input(f, filename)


if __name__ == '__main__':   
    pd.set_option('max_colwidth', 100)
    pd.set_option('colheader_justify', 'right')
    #pd.set_option(max_colwidth
    main()