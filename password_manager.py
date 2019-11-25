from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import json, base64, time, os
import pandas as pd


def gen_key(passwrd):
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(passwrd)
    return base64.urlsafe_b64encode(digest.finalize())

def read_file(fernet, filename):
    
    try:
        reader = open(filename, 'rb')
        content = reader.read()
        reader.close()
    except FileNotFoundError:
        print("Passwords' File not found in local directory.")
        return -1
        
    if len(content) > 1:
        try:
            decrypted_content = fernet.decrypt(content)
            print('Successful entry')            
            content = json.loads(decrypted_content)
            time.sleep(0.5)
            print('Entering Password Manager')
            time.sleep(0.5)
            return content
        except:
            time.sleep(0.5)
            print('Authentication Failed!')
            time.sleep(0.5)
            print('Exiting Password Manager...\n')
            time.sleep(0.2)
            return -1
    else:
        return {}


def update_file(passwords, f, filename):
    
    passwords_jsonized = json.dumps(passwords)        
    new_encr_passwords = f.encrypt(passwords_jsonized.encode())    
    
    reader = open(filename, 'wb')    
    reader.write(new_encr_passwords)
    reader.close()


def store_pass(fernet, filename, passwords):
   
    site = input('Site/App: ')
    userid = input('Userid: ')
    pasword = input('Password: ')
    other = input('Other details: ')

    #encrypted_pass = base64.urlsafe_b64encode(fernet.encrypt(pasword))  
    passwords[site] = {'User ID': userid, 'Password':  pasword, 'Other Details': other}
    update_file(passwords, fernet, filename)    
    

def change_password(passwords, filename):
    
    user_pass = input('Enter new decryption password: ').encode()
    key = gen_key(user_pass)
    f = Fernet(key)
    
    passwords_jsonized = json.dumps(passwords)        
    new_encr_passwords = f.encrypt(passwords_jsonized.encode())    
    
    reader = open(filename, 'wb')    
    reader.write(new_encr_passwords)
    reader.close()
    time.sleep(0.5)
    print('\nEncryption code changed')
    time.sleep(0.5)


def print_passwords(passwords):
    if len(passwords) > 0:
        df = pd.DataFrame(passwords).transpose()
        df = df[['User ID', 'Password', 'Other Details']]
        pd.set_option("display.max_rows", len(df))
        print('\n')
        print('-'*80)
        print('-'*20 +' '*11 + 'PASSWORDS DATABASE' +' '*11 +  '-'*20)
        print('-'*80)
        print(df)
        print('-'*80)
        print('\n')
        pd.reset_option('display.max_rows')
        input("Press Enter to continue...")
    else:
        print('No passwords stored')
    
    # ENTER CODE FOR USER INPUT BEFORE CONTINUING


def remove_password(passwords, f, filename):
    web = input('Choose website to delete password: ')
    if web in passwords.keys():
        del passwords[web]
        update_file(passwords,f,filename)
    else:
        time.sleep(0.5)
        print('\nPASSWORD NOT FOUND.')
        time.sleep(0.5)
    
def main_menu():
    print('\n')
    print('ENTER YOUR CHOICE FROM THE OPTIONS BELOW \n')
    print('\t"1": to see stored passwords')
    print('\t"2": to store a new password')
    print('\t"3": to remove an existing password')
    print('\t"4": to change the encryption code')
    print('\t"0": to exit to Desktop') 
        
    

def main():
    print('\n')
    print('-'*80)
    print('-'*20 +' '*10 + 'PASSWORD MANAGER v.1' +' '*10 +  '-'*20)
    print('-'*80)
    
    filename = 'passwords.txt'
    if os.path.exists(filename):
        user_pass = input('Enter decryption password: ').encode()

    else:
        print('File not found. Creating new file.')
        f=open(filename,'x')
        f.close()
        user_pass = input('Enter encryption password: ').encode()
        #exit()
    key = gen_key(user_pass)
    f = Fernet(key)
    
    passwords = read_file(f, filename)
    
    while(passwords != -1):
        
        main_menu()
        
        option = input('>: ')
        
        if option == '1':
            print_passwords(passwords)
        elif option == '2':
            store_pass(f, filename, passwords)
        elif option == '3':
            remove_password(passwords, f, filename)
        elif option == '4':
            change_password(passwords, filename)
        elif option == '0':
            break
        else:
            pass

if __name__ == '__main__':   
    main()
