#shopping list using Mysql database (Completed)

import mysql.connector as myc
import pickle
import platform

requireddatabase = 'shopping_data'
conn = None
username = None

try:
    pickle_in = open('udata.box','rb')
    userdata = pickle.load(pickle_in)
    pickle_in.close()
  
except:
    userdata = {'Trust': None, 'password': None, 'open' : 0, 'trustasked' : 'nope'}
    pickle_out = open('udata.box','wb')
    pickle.dump(userdata,pickle_out)
    pickle_out.close()

menu = """##############################################################################################
                    What do you want to do to your shopping list.. 
                    1]  View your shopping list.
                    2]  Add item to your shopping list.
                    3]  Remove an item from your shopping list.
                    4]  Clear the shopping list.
                    5]  Exit.
                    99] Trust or Forget device.
##############################################################################################
\n >>> """

def proceed(conn):
    global requireddatabase
    cursor = conn.cursor()
    cursor.execute("show databases")
    databases = cursor.fetchall()

    for i in range(len(databases)):
        if databases[i][0] == requireddatabase:
            cursor.execute("use " + requireddatabase )
            dataexists = True
            break
          
        else:
            dataexists = False

    if dataexists == False:
        cursor.execute("create database " + requireddatabase)
        cursor.execute("use " + requireddatabase)
        cursor.execute("create table shopping_list (Item varchar(20), Qty int, primary key(Item))")
      
    return cursor

#to convert tupled list to normal list
def purifylist(topurify):
    templist = []
    for i in range(len(topurify)):
        templist.append(topurify[i][0])
    return templist

def gettables(cursor):
    cursor.execute("select item from shopping_list")
    tables = cursor.fetchall()

    return purifylist(tables)

#option 1
def viewtable(cursor):
    if gettables(cursor) == []:
        print("The shopping list is empty\n")

    else:
        cursor.execute("select * from shopping_list")
        items_list = cursor.fetchall()
        for i in range(len(items_list)):
            print(f" {items_list[i][0]} {items_list[i][1]} Kgs   ")
      
#option 2
def insert(cursor,item,qty):
    global conn
    if item not in gettables(cursor):
        sqlcode = f"insert into shopping_list values( '{item}' , {qty})"
        cursor.execute(sqlcode )
        print(f"\n{item} added susessfully \n")
      
    else:
        while True:
            do = input(f"{item} already exists in the table, would you like to update its quantity? (y,n)\n")
            do = do.strip()
            do.lower()
        
            if do == 'y':
                removeqty(cursor,item,int(qty))
                break
              
            elif do == 'n':
                print(f'Dropping action to add {item}\n')
                break
            
            else:
                print("Please enter either y or n \n")
        viewtable(cursor)
    conn.commit()

#option 3 (1)
def removeitem(cursor,item):
    global conn
    cursor.execute("select item from shopping_list")
    items = cursor.fetchall()
    purifieditems = purifylist(items)
    
    if item not in purifieditems:
        print(f"{item} does not exist in the table \n")

    else:
        cursor.execute(f"delete from shopping_list where item = '{item}'")
        print(f"\n{item} removed susessfully \n")
    conn.commit()

#Establishing connection
def connect():
    global conn,userdata,upass
    run = True
    trustdevice = 0
    try:
        if userdata['Trust'] == 'Trust':
            trustdevice = 1
        else:
            trustdevice = 0
    except Exception as e:
        print(e,'nope not working\n')

    while True:
        try:
            if trustdevice == 0:
                upass = input("Enter password for your mysql database (user: root) \n")
                conn= myc.connect(host = 'localhost', user = 'root', passwd = upass)
                if userdata['trustasked'] == 'nope':
                    userdata['trustasked'] = 'yup'
                    asktrust = input("Trust this device? Enabling this lets you login without entering the  sql password.\n(y,n) >>> ")
                    
                    if asktrust.strip().lower() == 'y':
                        userdata['password'] = upass
                        userdata['Trust'] = 'Trust'

                    elif asktrust.strip().lower() == 'n':
                        print('Device not remembered\n')
                        
                    else:
                        print('Invalid action\n')
                        
                    pickle_out = open('udata.box','wb')
                    pickle.dump(userdata,pickle_out)
                    pickle_out.close()
                    
                else:
                    pass
                  
                return proceed(conn)
          
            else:
                while run:
                    try:
                        conn= myc.connect(host = 'localhost', user = 'root', passwd = userdata['password'])
                        run = False
                        return proceed(conn)
                    
                    except:
                        userdata = {'Trust': None, 'password': None, 'open' : 0, 'trustasked' : 'yup'}
                        pickle_out = open('udata.box','wb')
                        pickle.dump(userdata,pickle_out)
                        pickle_out.close()
                        return connect()
        
        except Exception as e:
            print(e,'error')

#option 3 (2)
def removeqty(cursor,item):
    global conn
    cursor.execute("select item from shopping_list")
    items = cursor.fetchall()
    purifieditems = purifylist(items)
    
    if item not in purifieditems:
        print(f"{item} does not exist in the table \n")

    else:
        while True:
            try:
                qty = int(input("Enter the quantity to update(in kgs) \n"))
                break
            
            except:
                print("Please enter a valid quantity to delete \n")
        if qty >0:
            cursor.execute(f"update shopping_list set qty = {qty} where item = '{item}'")
            print(f'{item} quantity updated to {qty} kgs \n')
          
        else:
            cursor.execute(f"update shopping_list set qty = 0 where item = '{item}'")
            print(f'{item} quantity updated to 0 \n')
        conn.commit()

#option 4 
def clear(cursor):
    global conn
    while True:
        sure = input("Would you like to clear the shopping_list (y,n):\n")
        sure = sure.strip()
        sure = sure.lower()
        
        if sure == 'y':
            cursor.execute('truncate table shopping_list')
            print("Data cleared successfully \nYour list is now empty\n")
            break
        
        elif sure == 'n':
            break
        
        else:
            print('Please enter a valid input \n')
    conn.commit()

#option 99
def trustorforget():
    global userdata,upass
    if userdata['Trust'] == 'Trust':
        ask = input('Would you like me to fotget this device \n(y,n) >>> ')
        if ask.strip().lower() == 'y':
            userdata['Trust'] = None
            userdata['password'] = None
            pickle_out = open('udata.box','wb')
            pickle.dump(userdata,pickle_out)
            pickle_out.close()
            print('Device forgotten \n')
        else:
            print('Forget device canceled \n')
    else:
        print("Trust device feature is already off for this device \n")
        ask = input('Would you like me to trust this device \n(y,n) >>> ')
        if ask.strip().lower() == 'y':
            upass = input("Enter your sql database password \n")
            userdata['Trust'] = 'Trust'
            userdata['password'] = upass
            pickle_out = open('udata.box','wb')
            pickle.dump(userdata,pickle_out)
            pickle_out.close()
            print('Device Trusted')
        elif ask.strip().lower() == 'n':
            print('Device not trusted\n')

def main():
  
    finalcursor = connect()
    
    while True:
        while True:
            try:
                todo = int(input(menu))
                break
            
            except:
                print("Please Enter a valid input \n")

        if todo == 1:
            viewtable(finalcursor)
        
        elif todo == 2:
            itemname = input("Enter item name \n")
            itemname = itemname.strip()
            itemname = itemname.upper()
            while True:
                try:
                    itemqty = int(input("Enter the quantity (in kgs) \n"))
                    break
                
                except:
                    print('please enter a valid quantity \n')
            insert(finalcursor,itemname,itemqty)

        elif todo == 3:
            while True:
              try:
                  delaction = int(input("would like to \n1) Remove the whole item  \n2) Update its quantity \n"))
                  break
                
              except:
                  print("Please enter a valid option\n")
            if delaction == 1:
                itemname = input("Enter the item name you want to delete \n")
                itemname = itemname.strip()
                itemname = itemname.upper()
                removeitem(finalcursor,itemname)

            elif delaction == 2:
                itemname = input("Enter the item name you want to update \n")
                itemname = itemname.strip()
                itemname = itemname.upper()
                removeqty(finalcursor,itemname)

        elif todo == 4:
            clear(finalcursor)
            
        elif todo == 5:
            conn.commit()
            print("Good bye :)")
            break

        elif todo == 99:
              trustorforget()
        
        else:
            print("Please enter a valid option\n")
        
      

main()
