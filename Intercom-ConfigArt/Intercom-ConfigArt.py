# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 23:36:38 2021

@author: DarkLegacy
"""
import threading
import math
import numpy as np
from tkinter import * # analysis:ignore
from tkinter import StringVar, PhotoImage, Menu
# from tkinter import *
from tkinter.ttk import * # analysis:ignore
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfile # analysis:ignore
# import tkinter.filedialog
from tkinter.filedialog import asksaveasfile
import tkinter as tk
import tkinter.font as TkFont
import pandas as pd
import os
import serial
from time import sleep
from serial.tools import list_ports

rootdataobj = None
rootdataself = None
read_flag = False
flag = False
Auth_Password = "1947"
SERIAL_PORT = None #"COM6"
BAUD_RATE = 115200
READ_TIMEOUT = 5
HW_FLOW_CONTROL = True
HANDSHAKE_REC_BYTE = b'\xAA'
HANDSHAKE_TX_BYTE = b'\x55'  
FILE_NAME = "./Data XLSX/temp.xlsx"
CMD_SHEET = "CmdData"
TX_DATA_SHEET = "ConfigData"
RX_DATA_SHEET = "ReadData"
FILE_FD = None
Read_Bytes = 24
Write_Bytes = 24
# CMD_SWITCHER = {0: No_Action, 1: Write_CMD, 2: Read_CMD, 3: Password_change}
VALUES = ['']*24
VALUES_R = [1]*24
to_byte1 = ['0']*16
to_byte2 = ['0']*16
byte_list1 = [0]*16
byte_list2 = [0]*16
dial_enab = ['0']*16
VALUES_B = list()
# VALUES_R = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
COMMAND_VALUE = 0

###############################################################--Root Window--###############################################################

root = tk.Tk()

app_width = 1535
app_height = 730

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = (screen_width/2) - (app_width/2)
y = (screen_height/2) - (app_height/2) - 50

# root.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
root.geometry('+%d+%d'%(x,y))
root.resizable(False, False)
root.title('ConfigArt')

bigfont = TkFont.Font(family="Helvetica",size=12)
root.option_add("*TCombobox*Font", bigfont) 

pd.set_option("display.max_columns",10)

data = pd.read_excel('./Data XLSX/data.xlsx')
data = data.replace(np.nan,"")

#################################################################--Variables--#############################################################

labelEntry = StringVar()
priority = StringVar()
deportedCheck = StringVar()
deportedPair = StringVar()
groupOption1 = StringVar()
groupOption2 = StringVar()
priorityB = StringVar()
priorityC = StringVar()
radioTF = StringVar()
password = StringVar()
password1 = StringVar()
password2 = StringVar()
password3 = StringVar()
trueFalse = StringVar()

options = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
pri_options = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
group2_options = [1,2,3,4,5,6,7,8]
group1_options = [9,10,11,12,13,14,15,16]

photo = PhotoImage(file='./Images/Marker0.png')
photo1 = PhotoImage(file='./Images/Marker1.png')
photo2 = PhotoImage(file='./Images/Radio0.png')
photo3 = PhotoImage(file='./Images/Radio1.png')

#-----------------------------------------------------------------------------------------#

'''
Function    : open_serial_port
Description : Opens serial port for read write operation
Return      : Serial port object
'''
def open_serial_port():
    try:
        serial_conn = serial.Serial( port = SERIAL_PORT, baudrate = BAUD_RATE, 
                                    timeout = READ_TIMEOUT )
        print(serial_conn)
        return serial_conn
    except ValueError:
        print("provide proper configuration")
        return None
    except serial.SerialException:
        print("cannot connect")
        return None
    except Exception as e:
        print(e)
        return None

'''
Function    : write_UART
Description : Write data into the serial port
'''
def write_UART( serial_conn, data ):
    serial_conn.write(data)

'''
Function    : read_UART
Description : Read data from serial port
Return      : Read data
'''
def read_UART( serial_conn ):
    read_data = serial_conn.read(size = 1)
    return read_data 

'''
Function    : handshaking_sig
Description : Sending the handshaking signal to the device after every 2sec,
              stop when receive responce from the device 
Return      : 
'''
def handshaking_sig(serial_conn):

    while True:

        rec_data = read_UART(serial_conn)
        # print("Receive signal from device ----",rec_data)
        sleep(0.001)
        if rec_data == HANDSHAKE_REC_BYTE:
            write_UART( serial_conn, HANDSHAKE_TX_BYTE )
            print("Received signal from device----------",rec_data)
            print("sending sig----",HANDSHAKE_TX_BYTE)
            #sleep(0.001)
            break
        
'''
Function    : serial_init
Description : Performs the initialization of serial port
Return      : serial port object
'''
def serial_init():    
    count = 5
    while count:
        count -= 1
        serial_conn = open_serial_port() 
        if serial_conn:
            break

    return serial_conn

'''
Function    : Get_CMD
Description : Read command from the file 
                0 - No action
                1 - Write Cmd
                2 - Read Cmd
                3 - Password change Cmd

Return      : Read command
'''
def Get_CMD():
    row = 1
    col = 1
    cmd_sheet = FILE_FD[CMD_SHEET] 

    cmd = int(float(str(cmd_sheet.cell(row,col).value)) )
    print("Command--- ",cmd)
    return cmd

'''
Function    : get_password_from_user
Description : Get password from the user as a input
Return      : None
'''

def subCallBack():
    trueFalse.set(True)
    
def valPass1():
    global flag, Auth_Password
    print("In Password Validation")
    if(len(password.get())!=4):
        messagebox.showerror("Enter Valid Password", "Password length can be only 4 Characters/Numbers")
        password.set("")
    else:
        Auth_Password = password.get()
        # Auth_Password = int(Auth_Password)
        flag=True
    
def func(event):
    print("You hit return.")
    valPass1()
    
def get_password_from_user(new):
    global Auth_Password
    
    print("In Get PAssword Tkinter")
    print(threading.currentThread().getName())
    
    entPass = ttk.Label(new, text="Enter Password", font=15, foreground='black', justify='left')
    entPass.grid(column=0, row=0, padx=10, pady=10, sticky='W')
    
    passw = tk.Entry(new, show="*", textvariable=password, font=("",12,""), relief="solid")
    passw.grid(column=1,row=0, padx=10, pady=10)
    password.set("")
    trueFalse.set(False)
    
    sub_btn=tk.Button(new, command=valPass1, text = 'Submit', font=("",10,"bold"), width=15)
    sub_btn.grid(column=1,row=1, padx=10, pady=10)
    new.bind('<Return>', func)
    
    return sub_btn
    


'''
Function    : validate_password
Description : Read password responce from the device 
              that indicates pasword is valid or invalid.
Return      : True - Password is valid
              False - Password is invalid  
'''
def validate_password( serial_conn ):
    rec_data = read_UART(serial_conn)
    print(rec_data)
    if rec_data == b'\xC8':
        rec_data = read_UART(serial_conn)
        print(rec_data, "INNNNNNN Here")

        if rec_data == b'\x01':
            rec_data = read_UART(serial_conn)
            print(rec_data)
            if rec_data == b'\xCA':
                print("Password validation successful-----")
                messagebox.showinfo("Validation Successful", "Password validation successful")
                return True
        elif rec_data == b'\x08':         
            rec_data = read_UART(serial_conn)
            print(rec_data)
            if rec_data == b'\xCA':
                print("Invalid Password-----")
                messagebox.showerror("Invalid Password", "Incorrect Password")
                return False
        else:
            messagebox.showerror("Invalid Password", "Incorrect Password")
            print("Password validation failed---")
            return False
        

def validate_password1( serial_conn ):
    rec_data = read_UART(serial_conn)
    print(rec_data)
    if rec_data == b'\xC8':
        rec_data = read_UART(serial_conn)
        print(rec_data, "INNNNNNN Here")

        if rec_data == b'\x01':
            rec_data = read_UART(serial_conn)
            print(rec_data)
            if rec_data == b'\xCA':
                print("Password validation successful-----")
                # messagebox.showinfo("Validation Successful", "Password validation successful")
                return True
        elif rec_data == b'\x08':         
            rec_data = read_UART(serial_conn)
            print(rec_data)
            if rec_data == b'\xCA':
                print("Invalid Password-----")
                # messagebox.showerror("Invalid Password", "Incorrect Password")
                return False
        else:
            # messagebox.showerror("Invalid Password", "Incorrect Password")
            print("Password validation failed---")
            return False    


'''
Function    : password_authentication
Description : Send user password to the device 
              and read responce from the device
Return      : True - Password is valid
              False - Password is invalid  
'''
def password_authentication(serial_conn):

    #Clear the UART buffer
    if serial_conn.in_waiting:
        print("UART buff bytes--",serial_conn.in_waiting)
        serial_conn.read(serial_conn.in_waiting)

    #Send password start command to the device
    write_UART( serial_conn, b'\xC8' )

    #Send user passsword to the device
    for ele in Auth_Password:
        d = ele.encode() #---2
        print(d,type(d))
        write_UART( serial_conn, d )

    #Send password end command to the device
    write_UART( serial_conn, b'\xCA' )
    sleep(0.001)
    
    #VAlidate the user password by reading device responce
    return validate_password( serial_conn )
    sleep(0.001)
    
    
def password_authentication1(serial_conn):

    #Clear the UART buffer
    if serial_conn.in_waiting:
        print("UART buff bytes--",serial_conn.in_waiting)
        serial_conn.read(serial_conn.in_waiting)

    #Send password start command to the device
    write_UART( serial_conn, b'\xC8' )

    #Send user passsword to the device
    for ele in Auth_Password:
        d = ele.encode() #---2
        print(d,type(d))
        write_UART( serial_conn, d )

    #Send password end command to the device
    write_UART( serial_conn, b'\xCA' )
    sleep(0.001)
    
    #VAlidate the user password by reading device responce
    return validate_password1( serial_conn )
    sleep(0.001)
    
    
'''
Function    : COM_port_list
Description : Find the list of COM port and use first port for the communication.
Return      : True - COM port is available
              False - COM port is not available 
'''
def COM_port_list():
    global SERIAL_PORT
    port_list = []
    try: 
        all_port_tuples = list_ports.comports()
        print(all_port_tuples)
        for ap, _, _ in all_port_tuples:
            print(ap)
            port_list.append( os.path.basename(ap) )
        print(port_list)
        SERIAL_PORT = port_list[len(port_list) - 1]
        return True
    except Exception as e:
        print(e)
        return False    


'''
Function    : get_configuration
Description : Get COM port and Open file for communication
Return      : True - Successful to read configuration
              False - Fail to read configuration
'''
def get_configuration():
    if not COM_port_list():
        print("COM port not detected--")
        return False
    
    return True     

'''
Function    : No_Action
Description : Don't do anything
Return      : None
'''
def No_Action(temp):
    print("No Action---Over here")

'''
Function    : Read_CMD
Description : Read data from device through UART and write in to the file.
Return      : None
'''
def Read_CMD(serial_conn):
    global VALUES_R, dial_enab, byte_list1, byte_list2
    print("Read_CMD----")
    
    try: 
        #Sending Read command to the device
        write_UART( serial_conn, b'\xC8' )
        write_UART( serial_conn, b'\x03' )
        write_UART( serial_conn, b'\xCA' )
        sleep(0.001)
    
        for i in range(Read_Bytes):
            data = read_UART(serial_conn)
            print(data,ord(data))
            VALUES_R[i] = ord(data)
    
        data = read_UART(serial_conn)
        print(data,ord(data),"call restriction started")
        cnt = 0
        for i in range(32):
            data = read_UART(serial_conn)
            print(data,ord(data))
            if(i%2==0):
                byte_list1[cnt] = ord(data)
            else:
                byte_list2[cnt] = ord(data)
                cnt+=1
            
        print("Call restrictions Read Complete")
    
        for i in range(16):
            data = read_UART(serial_conn)
            print(data,ord(data))
            dial_enab[i] = ord(data)
    
        print("Dial 9 enable Read complete")
        
        rootdataobj.readToData()
        print("Read operation successful----")
        messagebox.showinfo("", "Data Read Successfull")
        
    except Exception as e:
        messagebox.showerror("", "Data Read Failure")
        VALUES_R = [0]*24
        print(e)
        print("Read operation fail----")

'''
Function    : Write_CMD
Description : Read data from file and send to the device through UART.
Return      : None
'''
def Write_CMD(serial_conn):
    print("Write_CMD----")
    global VALUES
    try:
        #Sending write command to the device
        write_UART( serial_conn, b'\xC8' )
        write_UART( serial_conn, b'\x02' )
        write_UART( serial_conn, b'\xCA' )
        sleep(0.001)
        
        for i in VALUES:
            data = i
            VALUES_B.append(bytes([data]))
            print("----",bytes([data]))
            #Send read data to the device
            write_UART( serial_conn,bytes([data]))
        
        write_UART(serial_conn, bytes([200]))
        sleep(1)
        print("Caller Restriction Started")
        
        for i in range(16):
            print("----",bytes([to_byte1[i]]))
            print("----",bytes([to_byte2[i]]))
            print()
            write_UART(serial_conn, bytes([to_byte1[i]]))
            write_UART(serial_conn, bytes([to_byte2[i]]))
        
        print("Dial 9 Started")
        
        for i in range(16):
            print("----",bytes([dial_enab[i]]))
            write_UART(serial_conn, bytes([dial_enab[i]]))
        
        write_UART(serial_conn, bytes([202]))
        
        print("Write operation successful----")
    except Exception as e:
        print(e)
        print("Write operation fail----")        

'''
Function    : Password_change
Description : Change device password.
Return      : None
'''
def Password_change(serial_conn):
    print("Password Change command----")

'''
Function    : perform_action
Description : Read command from the file and perform the action accordingly
Return      : None
'''
def perform_action(serial_conn):
    CMD_SWITCHER = {
    0: No_Action,
    1: Write_CMD,
    2: Read_CMD,
    3: Password_change
    }
    cmd = COMMAND_VALUE
    CMD_SWITCHER.get(cmd, "Invalid Command--")(serial_conn)
    

def changePasswordBackEnd(serial_conn):
    print("In Chagne Pass Back end")
    write_UART( serial_conn, b'\xC8' )
    write_UART( serial_conn, b'\x04' )
    write_UART( serial_conn, b'\xCA' )
    
    sleep(0.1)
    
    write_UART( serial_conn, b'\xC8' )
    for ele in Auth_Password:
        d = ele.encode() #---2
        print(d,type(d))
        write_UART( serial_conn, d )
    write_UART( serial_conn, b'\xCA' )

    # sleep(0.1)
    flag = validate_password1(serial_conn)
    if(flag==True):
        messagebox.showinfo("Password Change Successul","Password Changed Succesfully.")
        for i in range(4):
            data = read_UART(serial_conn)
            print(data,ord(data))
    else:
        messagebox.showerror("No Acknowledgement Recieved","No acknowledgement recieved from the device.")



'''
Function    : main
Return      : None
'''    

def main1(new):   
    
    print("In Main")
    
    # Get COM port and open file
    get_configuration()
     
    # Opening  serial port for communication
    serial_conn = serial_init()
    
    while flag==False:
        sleep(0.1)
        
    if(flag==True):
        new.destroy()
     
    # Sending handshaking signal to the device
    handshaking_sig(serial_conn)  
    if password_authentication(serial_conn):
        # Perform action according to command receive from file
        perform_action(serial_conn)
    
    print("End")
    
    
def mainForPasswordChange():   
    
    print("In Main mainForPasswordChange")
    
    # Get COM port and open file
    get_configuration()
     
    # Opening  serial port for communication
    serial_conn = serial_init()
     
    # Sending handshaking signal to the device
    handshaking_sig(serial_conn)  
    if password_authentication1(serial_conn):
        return True,serial_conn
    return False,serial_conn
    
    print("End")

############################################################--Root Functions--########################################################

def open_win(i):
    new = tk.Toplevel(root)
    # new.geometry('812x370')
    new.resizable(False, False)
    new.title('Configuration Setting')
    # new.attributes('-topmost',True)
    app_width = 900
    app_height = 430
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = (screen_width/2) - (app_width/2)
    y = (screen_height/2) - (app_height/2)
    
    # new.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
    new.geometry('+%d+%d'%(x,y))
    labelEntry = StringVar()
    priority = StringVar()
    deportedCheck = StringVar()
    deportedPair = StringVar()
    labEnt = data.iloc[i-1]["Label"]
    priVar = int(data.iloc[i-1]["Priority"])
    depPai = data.iloc[i-1]["Deported"]
    grpRes = data.iloc[i-1]["Group Restrictions"]
    groupDial = data.iloc[i-1]["Dial 9 Number"]
    dial9Ena = data.iloc[i-1]["Dial 9 Enable"]
    
    
    deportedSplit = depPai.split(",")
    labelEntry.set(labEnt)
    priority.set(priVar)
    deportedCheck.set(deportedSplit[0])

    if(len(deportedSplit)==2):
        try:
            deportedPair.set(int(deportedSplit[1]))
        except:
            deportedPair.set(int(0))
    
    # new.grab_set_global()
    
    
    
    obj = PortConfig()
    obj.createFrame(new)
    obj.setter(new, root, index=i, labelEntry=labelEntry, priority=priority, deportedCheck=deportedCheck, deportedPair=deportedPair, grpRes=grpRes, groupDial=int(groupDial), dial9Ena = dial9Ena)
    obj.labelFun(new)
    obj.dropdownFun(new)
    obj.entryFun(new)
    obj.buttonFun(new)
    obj.radioFun(new)

def remove_items(test_list, item):
    # remove the item for all its occurrences
    for i in test_list:
        if(i == item):
            test_list.remove(i)
  
    return test_list    

def open_file1():
    global data,root
    filename = askopenfile(title="Open a File", filetype=(("xlxs files", ".*xlsx"), ("All Files", "*.")))
    print(filename)
    data = pd.read_excel(filename.name)
    data = data.replace(np.nan,"")
    rt = RootData(root)
    rt.loadData(root)            


def save_file():
    data.to_excel('./Data XLSX/data.xlsx', index=False)
    
def save_as_file():
    files = [('Excel Files', '*.xlsx'), ('All Files', '*.*')]
    file = asksaveasfile(filetypes = files, defaultextension = data)
    data.to_excel(file.name, index=False)

#################################################################--Root Data--##########################################################

class RootData:
    
    root = None
    value = ['']*24
    index = 0
    chanNew = None
    
    def __init__(self, root):
        self.root = root
    
    def priorityBroadcast(self, event):
        data.at[0,"Values"] = int(priorityB.get())
        self.loadData(self.root)
    
    def priorityCalls(self, event):
        data.at[1,"Values"] = int(priorityC.get())
        self.loadData(self.root)
    
    def readToData(self):
        global COMMAND_VALUE, VALUES_R, dial_enab, byte_list1, byte_list2
        port_no = VALUES_R[1]
        deported_pair = VALUES_R[2]
        grp1_dial9 = VALUES_R[3]
        grp2_dial9 = VALUES_R[4]
        pri_val = []
        for i in range(16):
            pri_val.append(VALUES_R[5+i])
        pri_broad = VALUES_R[-3]
        pri_call = VALUES_R[-2]
        data["Label"] = ""
        data["Deported"] = 'No'
        data["Dial 9 Enable"] = 'Yes'
        data.at[0:8,"Dial 9 Number"] = grp1_dial9
        data.at[8:15,"Dial 9 Number"] = grp2_dial9
        data["Priority"] = pri_val
        data.at[0, "Values"] = int(pri_broad)
        data.at[1, "Values"] = int(pri_call)
        data.at[port_no-1,"Deported"] = "Yes, {}".format(deported_pair)
        
        # byte_list1 = [b'0xaa', b'0xff', b'0x0', b'0xff', b'0xff', b'0xff', b'0xff', b'0xff', b'0x33', b'0xff', b'0xff', b'0xff', b'0xff', b'0xff', b'0xff', b'0x1c']
        # byte_list2 = [b'0xaa', b'0xff', b'0x0', b'0xff', b'0xff', b'0xff', b'0xff', b'0xff', b'0x33', b'0xff', b'0xff', b'0xff', b'0xff', b'0xff', b'0xff', b'0x71']
        bin_list = [0]*16

        
        for i in range(16):
            temp1 = ""
            temp2 = bin(int(byte_list1[i]))
            temp3 = ""
            temp4 = bin(int(byte_list2[i]))
            temp2 = temp2[2:]
            temp4 = temp4[2:]
            len1 = len(temp2)
            len2 = len(temp4)
            if(len1 != 8):
                no = 8 - len1
                temp1 = '0'*no + temp2 
                temp2 = temp1
            
            if(len2 != 8):
                no = 8 - len2
                temp3 = '0'*no + temp4 
                temp4 = temp3
            
            bin_list[i] = temp2 + temp4 
            # print(temp2,temp4)

        print(bin_list)        
    
        call_res = [0]*16
        for i in range(16):
            temp = ""
            for j in range(16):
                if(bin_list[i][j] == "1"):
                    temp = temp + str(j+1) + ","
            call_res[i] = temp[0:-1]
        print(call_res)
        
        data["Group Restrictions"] = call_res
        
        # dial_enab = [0]*16
        # dial_list = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        dial_list = dial_enab
        
        for i in range(len(dial_list)):
            if dial_list[i] == 1:
                dial_enab[i] = "Yes"
            else:
                dial_enab[i] = 'No'
        
        print(dial_enab)
        data["Dial 9 Enable"] = dial_enab        
        
        self.loadData(self.root)
    
    def readData(self):
        global COMMAND_VALUE, VALUES_R, flag
        new = tk.Toplevel(root)
        new.resizable(False, False)
        new.title('Enter Password')
        app_width = 345
        app_height = 95
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        x = (screen_width/2) - (app_width/2)
        y = (screen_height/2) - (app_height/2)
        
        new.geometry('+%d+%d'%(x,y))
        # new.attributes('-topmost',True)
        t3 = threading.Thread(target=main1, args=(new,), name="T3")
        t4 = threading.Thread(target=get_password_from_user, args=(new,), name="T4")
        COMMAND_VALUE = 2
        new.grab_set()
        flag = False
        t4.start()
        sleep(0.1)
        t3.start()
        # self.readToData()
        
    
    def toExcel(self):
        global flag, to_byte1, to_byte2, dial_enab
        new = tk.Toplevel(root)
        new.resizable(False, False)
        new.title('Enter Password')
        # new.attributes('-topmost',True)
        app_width = 345
        app_height = 95
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        x = (screen_width/2) - (app_width/2)
        y = (screen_height/2) - (app_height/2)
        
        new.geometry('+%d+%d'%(x,y))
        t1 = threading.Thread(target=main1, args=(new,), name="T1")
        t2 = threading.Thread(target=get_password_from_user, args=(new,), name="T2")
        deported = list(data["Deported"])
        new.grab_set()
        for i in range(len(deported)):
            if('Yes' in deported[i]):
                print(deported[i],i+1)
                self.value[1]=i+1
                tp = deported[i].split()
                self.value[2]=int(tp[1])
        self.value[0]=200
        self.value[3]=data["Dial 9 Number"][3]
        self.value[4]=data["Dial 9 Number"][11]
        for i in range(len(data["Priority"])):
            self.value[i+5] = data["Priority"][i]
        
        self.value[-3] = int(priorityB.get())
        self.value[-2] = int(priorityC.get())
        self.value[-1] = 202
        print(self.value)
        tempTF = ""
        for i in deported:
            if("Yes" in i):
                tempTF=True
                break
            else:
                tempTF=False
        
        if(tempTF == False):
            messagebox.showerror("Warning", "There is no deported marked as 'Yes'")
            
        global VALUES, COMMAND_VALUE
        VALUES = self.value
        COMMAND_VALUE = 1
        
        port_grp_rest = ["0"]*16
        for i in range(16):
            grp_res = data.at[i,"Group Restrictions"].split(",")
            st = ""
            for j in range(16):
                if(str(j+1) in grp_res):
                    st = st + "1"
                else:
                    st = st + "0"
            port_grp_rest[i] = st
            
        print(port_grp_rest)
        
        for i in range(16):
            by = int(port_grp_rest[i],2)
            to_byte1[i] = math.floor(by/256)
            to_byte2[i] = by%256
        
        print()
        print(to_byte1)
        print(to_byte2)
        
        # dial_enab = [0]*16
        dial_list = list(data["Dial 9 Enable"])
        
        for i in range(len(dial_list)):
            if dial_list[i] == "Yes":
                dial_enab[i] = 1
            else:
                dial_enab[i] = 0
        
        print(dial_enab)
        
        Write_CMD(None)
        
        
        t1.start()
        t2.start()
        # main1(None)
        flag = False

    
    def setDial9Dashboard1(self, event):
        for j in range(8): 
            data.at[j,"Dial 9 Number"]=groupOption1.get()
        self.loadData(self.root)
        
    def setDial9Dashboard2(self, event):
        for j in range(9,17):
            data.at[j-1,"Dial 9 Number"]=groupOption2.get()
        self.loadData(self.root)
    
    def getData(self, string, num1, index):
        grpResStr = ""
        self.index = index
        print(string)
        for i in range(len(num1)-1,-1,-1):
            if(num1[i]==1):
                grpResStr = str(i+1) + ","  + grpResStr
        stringList = string.split(":,:")
        data.at[index-1,"Label"]=stringList[0]
        data.at[index-1,"Priority"]=stringList[1]
        depCol1 = list(data["Deported"])
        if(stringList[2]=='Yes'):
            for i in range(len(depCol1)):
                if('yes' in depCol1[i].lower() and i+1!=index):
                    data.at[i,"Deported"]='No'
                    messagebox.showerror("showerror", "Only one port can be set as deported at a time, discarding deported setting at Port No {}".format(i+1))
            data.at[index-1,"Deported"]=stringList[2]+", "+stringList[3]
        else:
            data.at[index-1,"Deported"]=stringList[2]    
        print(stringList)
        
        if(stringList[4].lower()=='yes'):
            data.at[index-1,"Dial 9 Enable"]=stringList[4]
            if(index<9):
                for j in range(8): 
                    data.at[j,"Dial 9 Number"]=int(stringList[5])
            else:
                for j in range(9,17):
                    data.at[j-1,"Dial 9 Number"]=int(stringList[6])
        else:
            data.at[index-1,"Dial 9 Enable"]=stringList[4]
        # print(data.at[index-1,"Deported"])
        data.at[index-1,"Group Restrictions"]=grpResStr[:-1]
        self.loadData(self.root)
        
    def valPass2(self):
        global Auth_Password, COMMAND_VALUE
        p1 = str(password1.get())
        p2 = str(password2.get())
        p3 = str(password3.get())
        
        if(len(p2)!=4 or len(p3)!=4):
            messagebox.showerror("Enter Valid Password", "Password length can be only 4 Characters/Numbers")
            password1.set("")
            password2.set("")
            password3.set("")
        if(p2!=p3):
            messagebox.showerror("Password Dosen't Match", "New Passwords dosen't match. ")
            password1.set("")
            password2.set("")
            password3.set("")
        if(p2==p3 and len(p2)==4 and len(p3)==4):
            print(p1,p2,p3,Auth_Password)
            Auth_Password = p1
            print(p1,p2,p3,Auth_Password)
            COMMAND_VALUE = 0
            flag,serial = mainForPasswordChange()
            if(flag!=True):
                 messagebox.showerror("Incorrect Password","Wrong Old Password")
                 password1.set("")
                 password2.set("")
                 password3.set("")
            else:
                Auth_Password = p2
                self.chanNew.destroy()
                changePasswordBackEnd(serial)
       
    
    def func(self,event):
        print("You hit return.")
        self.valPass2()
        
    def changePass(self):
        new = tk.Toplevel(root)
        new.resizable(False, False)
        new.title('Change Password')
        # new.attributes('-topmost',True)
        app_width = 392
        app_height = 175
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        x = (screen_width/2) - (app_width/2)
        y = (screen_height/2) - (app_height/2)
        
        new.geometry('+%d+%d'%(x,y))
        new.grab_set()
        password1.set("")
        password2.set("")
        password3.set("")

        entPass1 = ttk.Label(new, text="Old Password", font=10, foreground='black', justify='left')
        entPass1.grid(column=0, row=0, padx=10, pady=10, sticky='W')
        separator = ttk.Separator(new, orient='horizontal')
        separator.grid(row=1,sticky="ew")
        entPass2 = ttk.Label(new, text="New Password", font=10, foreground='black', justify='left')
        entPass2.grid(column=0, row=2, padx=10, pady=10, sticky='W')
        entPass3 = ttk.Label(new, text="Confirm New Password", font=10, foreground='black', justify='left')
        entPass3.grid(column=0, row=3, padx=10, pady=10, sticky='W')
        
        passw1 = tk.Entry(new, show="*", textvariable=password1, font=("",12,""), relief="solid")
        passw1.grid(column=1,row=0, padx=10, pady=10)
        separator = ttk.Separator(new, orient='horizontal')
        separator.grid(column=1, row=1,sticky="ew")
        passw2 = tk.Entry(new, show="*", textvariable=password2, font=("",12,""), relief="solid")
        passw2.grid(column=1,row=2, padx=10, pady=10)
        passw3 = tk.Entry(new, show="*", textvariable=password3, font=("",12,""), relief="solid")
        passw3.grid(column=1,row=3, padx=10, pady=10)
        self.chanNew = new
        sub_btn=tk.Button(new, command=self.valPass2, text = 'Submit', font=("",10,"bold"))
        sub_btn.grid(column=1,row=4, padx=10, pady=10)
        new.bind('<Return>', self.func)

    def loadData(self,root):
        portNo = list(data["Port No"])
        labCol = list(data["Label"])
        priCol = list(data["Priority"])
        depCol = list(data["Deported"])
        diaEna = list(data["Dial 9 Enable"])
        diaCol = list(data["Dial 9 Number"])
        grpCol = list(data["Group Restrictions"])
        
        col1 = tk.Label(root, text="Port No.", font=("",15,'bold'), foreground='black', width=12, background="gainsboro", relief="solid")
        col1.grid(row=0,column=1, padx=10, pady=10)
        col2 = tk.Label(root, text="Label", font=("",15,'bold'), foreground='black', width=12, background="gainsboro", relief="solid")
        col2.grid(row=0,column=2, padx=10, pady=10)
        col3 = tk.Label(root, text="Priority", font=("",15,'bold'), foreground='black', width=12, background="gainsboro", relief="solid")
        col3.grid(row=0,column=3, padx=10, pady=10)
        col4 = tk.Label(root, text="Deported", font=("",15,'bold'), foreground='black', width=12, background="gainsboro", relief="solid")
        col4.grid(row=0,column=4, padx=10, pady=10)
        col5 = tk.Label(root, text="Dial 9 Enable", font=("",15,'bold'), foreground='black', width=16, background="gainsboro", relief="solid")
        col5.grid(row=0,column=5, padx=10, pady=10)
        col6 = tk.Label(root, text="Dial 9 Number", font=("",15,'bold'), foreground='black', width=16, background="gainsboro", relief="solid")
        col6.grid(row=0,column=6, padx=10, pady=10)
        col7 = tk.Label(root, text="Call Restrictions", font=("",15,'bold'), foreground='black', width=19, background="gainsboro", relief="solid")
        col7.grid(row=0,column=7, padx=10, pady=10)
    
        lab = tk.Label(root, text="Group No. 1", font=("",10,'bold'), foreground='Black', height=15, width=15, background="cornflower blue", relief="groove")
        lab.grid(row=1, column=0, rowspan=8, padx=10)   
        
        btn1 = tk.Button(root, text="Port No 1", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(1))
        btn1.grid(row=1, column=1, padx=2, pady=2)
        btn2 = tk.Button(root, text="Port No 2", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(2))
        btn2.grid(row=2, column=1, padx=2, pady=2)
        btn3 = tk.Button(root, text="Port No 3", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(3))
        btn3.grid(row=3, column=1, padx=2, pady=2)
        btn4 = tk.Button(root, text="Port No 4", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(4))
        btn4.grid(row=4, column=1, padx=2, pady=2)
        btn5 = tk.Button(root, text="Port No 5", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(5))
        btn5.grid(row=5, column=1, padx=2, pady=2)
        btn6 = tk.Button(root, text="Port No 6", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(6))
        btn6.grid(row=6, column=1, padx=2, pady=2)
        btn7 = tk.Button(root, text="Port No 7", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(7))
        btn7.grid(row=7, column=1, padx=2, pady=2)
        btn8 = tk.Button(root, text="Port No 8", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(8))
        btn8.grid(row=8, column=1, padx=2, pady=2)
        lab5 = tk.Label(root, text="", foreground='black', width=20, height=2)
        lab5.grid(row=9, column=1, padx=2, pady=2)
        btn9 = tk.Button(root, text="Port No 9", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(9))
        btn9.grid(row=10, column=1, padx=2, pady=2)
        btn10 = tk.Button(root, text="Port No 10", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(10))
        btn10.grid(row=11, column=1, padx=2, pady=2)
        btn11 = tk.Button(root, text="Port No 11", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(11))
        btn11.grid(row=12, column=1, padx=2, pady=2)
        btn12 = tk.Button(root, text="Port No 12", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(12))
        btn12.grid(row=13, column=1, padx=2, pady=2)
        btn13 = tk.Button(root, text="Port No 13", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(13))
        btn13.grid(row=14, column=1, padx=2, pady=2)
        btn14 = tk.Button(root, text="Port No 14", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(14))
        btn14.grid(row=15, column=1, padx=2, pady=2)
        btn15 = tk.Button(root, text="Port No 15", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(15))
        btn15.grid(row=16, column=1, padx=2, pady=2)
        btn16 = tk.Button(root, text="Port No 16", font=("",8,'bold'), width=20, foreground='black', background="dodger blue", relief="raise", command=lambda:open_win(16))
        btn16.grid(row=17, column=1, padx=2, pady=2)
        
        for i in range(1,len(portNo)+2):
            if(i<9):
                lab2 = tk.Label(root, text=labCol[i-1], foreground='black', width=20, relief="groove")
                lab2.grid(row=i, column=2, padx=2, pady=2)
                lab3 = tk.Label(root, text=priCol[i-1], foreground='black', width=20, relief="groove")
                lab3.grid(row=i, column=3, padx=2, pady=2)
                lab4 = tk.Label(root, text=depCol[i-1], foreground='black', width=20, relief="groove")
                lab4.grid(row=i, column=4, padx=2, pady=2)
                lab5 = tk.Label(root, text=diaEna[i-1], foreground='black', width=27, relief="groove")
                lab5.grid(row=i, column=5, padx=2, pady=2)
                lab6 = tk.Label(root, text=diaCol[i-1], foreground='black', width=27, relief="groove")
                lab6.grid(row=i, column=6, padx=2, pady=2)
                lab7 = tk.Label(root, text=grpCol[i-1], foreground='black', width=32, relief="groove")
                lab7.grid(row=i, column=7, padx=2, pady=2)
            elif(i==9):
                lab5 = tk.Label(root, text="", foreground='black', width=32, height=2)
                lab5.grid(row=9, column=6, padx=2, pady=2)
                lab5 = tk.Label(root, text="________________________________________________________________________________________________________________________________________________________________________________________________________________________", font=("",10,'bold'), foreground='black')
                lab5.place(x=8,y=295)
            else:
                lab2 = tk.Label(root, text=labCol[i-2], foreground='black', width=20, relief="groove")
                lab2.grid(row=i, column=2, padx=2, pady=2)
                lab3 = tk.Label(root, text=priCol[i-2], foreground='black', width=20, relief="groove")
                lab3.grid(row=i, column=3, padx=2, pady=2)
                lab4 = tk.Label(root, text=depCol[i-2], foreground='black', width=20, relief="groove")
                lab4.grid(row=i, column=4, padx=2, pady=2)
                lab5 = tk.Label(root, text=diaEna[i-2], foreground='black', width=27, relief="groove")
                lab5.grid(row=i, column=5, padx=2, pady=2)
                lab6 = tk.Label(root, text=diaCol[i-2], foreground='black', width=27, relief="groove")
                lab6.grid(row=i, column=6, padx=2, pady=2)
                lab7 = tk.Label(root, text=grpCol[i-2], foreground='black', width=32, relief="groove")
                lab7.grid(row=i, column=7, padx=2, pady=2)        
                
        lab = tk.Label(root, text="Group No. 2", font=("",10,'bold'), foreground='black', height=15, width=15, background="cornflower blue", relief="groove")
        lab.grid(row=10, column=0, rowspan=8, padx=10)
        
        ##############################################################--Root Buttons--##########################################################
        
        lab5 = tk.Label(root, text="", foreground='black')
        lab5.grid(row=18, column=0, padx=2, pady=2)
        
        load = tk.Button(root, text="Load", font=("",8,'bold'), width=16, foreground='black', background="dodger blue", relief="raise", command=self.toExcel)
        load.grid(row=19, column=0, padx=2, pady=2)
        
        read = tk.Button(root, text="Read", font=("",8,'bold'), width=16, foreground='black', background="dodger blue", relief="raise", command=self.readData)
        read.grid(row=20, column=0, padx=2, pady=2)
        
        chan = tk.Button(root, text="Change Password", font=("",8,'bold'), width=16, foreground='black', background="dodger blue", relief="raise", command=self.changePass)
        chan.grid(row=21, column=0, padx=2, pady=2)
        
        label7 = ttk.Label(root, text="Group 1 Dial 9", font=8, foreground='black')
        label7.grid(column=6, row=20, padx=15, pady=10, sticky='E')
        
        label8 = ttk.Label(root, text="Group 2 Dial 9", font=8, foreground='black')
        label8.grid(column=6, row=21, padx=15, pady=10, sticky='E')
        
        drop6 = ttk.Combobox(root, state="readonly", values=group1_options, textvariable=groupOption1)
        
        groupOption1.set(data["Dial 9 Number"][3])
        drop6.grid(column=7,row=20, padx=10, pady=10, sticky='W')
        drop6.bind("<<ComboboxSelected>>",lambda e: lab5.focus())
        drop6.bind("<<ComboboxSelected>>", self.setDial9Dashboard1)
        drop7 = ttk.Combobox(root, state="readonly", values=group2_options, textvariable=groupOption2)
        groupOption2.set(data["Dial 9 Number"][11])
        drop7.grid(column=7,row=21, padx=10, pady=10, sticky='W')
        drop7.bind("<<ComboboxSelected>>",lambda e: lab5.focus())
        drop7.bind("<<ComboboxSelected>>", self.setDial9Dashboard2)
        
        label9 = ttk.Label(root, text="Priority of BC", font=8, foreground='black')
        label9.grid(column=4, row=20, padx=15, pady=10, sticky='E')
        label10 = ttk.Label(root, text="Priority of PC", font=8, foreground='black')
        label10.grid(column=4, row=21, padx=15, pady=10, sticky='E')
        drop8 = ttk.Combobox(root, state="readonly", values=pri_options, textvariable=priorityB)
        priorityB.set(data["Values"][0])
        drop8.grid(column=5,row=20, padx=10, pady=10, sticky='W')
        drop8.bind("<<ComboboxSelected>>",lambda e: label9.focus())
        drop8.bind("<<ComboboxSelected>>", self.priorityBroadcast)
        drop9 = ttk.Combobox(root, state="readonly", values=pri_options, textvariable=priorityC)
        priorityC.set(data["Values"][1])
        drop9.grid(column=5,row=21, padx=10, pady=10, sticky='W')
        drop9.bind("<<ComboboxSelected>>",lambda e: label10.focus())
        drop9.bind("<<ComboboxSelected>>", self.priorityCalls)


#########################################################--Port Config Class--##########################################################

class PortConfig:

    num = 1
    num1 = [1]*16
    rad = [True]*16
    radNums = [1]*16
    tF = ""
    dial9Var = ""
    index = 0
    root = None
    new = None
    frame1 = None
    frame2 = None
    
    labelEntry = StringVar()
    priority = StringVar()
    deportedCheck = StringVar()
    dial91 = StringVar()
    dial92 = StringVar()
    deportedPair = StringVar()
    groupOption1 = StringVar()
    groupOption2 = StringVar()
    radioTF = StringVar()
    
    drop2 = ttk.Combobox()
    drop3 = ttk.Combobox()
    check1 = tk.Button()
    dial91TF = tk.Button()
    radio1 = tk.Button()
    radio2 = tk.Button()
    radio3 = tk.Button()
    radio4 = tk.Button()
    radio5 = tk.Button()
    radio6 = tk.Button()
    radio7 = tk.Button()
    radio8 = tk.Button()
    radio9 = tk.Button()
    radio10 = tk.Button()
    radio11 = tk.Button()
    radio12 = tk.Button()
    radio13 = tk.Button()
    radio14 = tk.Button()
    radio15 = tk.Button()
    radio16 = tk.Button()
    
    
    def __init__(self):
        self.num = 1
        self.num1 = [1]*16
        self.rad = [True]*16 
        
        
    def createFrame(self,new):
        frame1 = tk.LabelFrame(new, borderwidth=0)
        frame1.grid(column=0, row=0, padx=10, pady=10, sticky='W')
        self.frame1 = frame1
        
        frame2 = tk.LabelFrame(new, borderwidth=0)
        frame2.grid(column=0, row=1, padx=10, pady=10, sticky='W')
        self.frame2 = frame2
        
    def setter(self, new, root, index=None, labelEntry=StringVar(), priority=StringVar(), deportedCheck=StringVar(), deportedPair=StringVar(), groupOption1=StringVar(), groupOption2=StringVar(), grpRes=None, groupDial=None, dial9Ena=""):
        try:
            self.new = new
            self.labelEntry = labelEntry
            self.priority = priority
            self.deportedCheck = deportedCheck
            self.deportedPair = deportedPair
            self.groupOption1.set(int(groupDial))
            self.groupOption2.set(int(groupDial))
            self.tF = deportedCheck.get()
            self.index = index
            self.root = root
            self.dial9Var = dial9Ena
            self.new.grab_set()
            if(deportedCheck.get()=='Yes'):
                self.checkFun(new,var=1)
            else:
                self.checkFun(new,var=0)
            groupRest = list(map(int, grpRes.split(",")))
            for i in range(17):
                if(i in groupRest):
                    self.num1[int(i)-1]=1
                else:
                    self.num1[int(i)-1]=0
        except:
            print('error')
            
    def getter(self):
        global rootdataobj
        rt = RootData(self.root)
        
        da = self.labelEntry.get() + ":,:" + self.priority.get() + ":,:" + self.deportedCheck.get() + ":,:" + self.deportedPair.get() + ":,:" + self.dial9Var + ":,:" + self.groupOption1.get() + ":,:" + self.groupOption2.get()
        print(da)
        rt.getData(da, self.num1, self.index)
        
    def submit(self):
        if(self.num==0):
            self.tF='Yes'
        else:
            self.tF='No'
        if(self.num==1):
            self.tF='Yes'
        else:
            self.tF='No'
            
        if(self.deportedCheck.get().lower()=="yes" and self.deportedPair.get()==""):
            messagebox.showerror("Error", "Cannot leave Deported Pair Empty")
            return None
        
        for i in range(len(self.num1)):
            if(self.num1[i]==1):
                self.rad[i]=True
            else:
                self.rad[i]=False        
        self.getter()
        self.new.destroy()
    
    def dial9Fun(self): 
        if(self.dial9Var=='No'):
            self.dial91TF.configure(image=photo1)
            self.dial9Var = 'Yes'
            self.drop3.configure(state="readonly")
        else:
            self.dial91TF.configure(image=photo)
            self.dial9Var = 'No'
            self.drop3.configure(state="disabled")
    
    def change_pic(self): 
        if(self.num==1):
            self.check1.configure(image=photo1)
            self.num-=1
            self.deportedCheck.set("Yes")
            print("num",self.num)
            self.drop2.configure(state="readonly")
        else:
            self.check1.configure(image=photo)
            self.num+=1
            self.deportedCheck.set("No")
            print("num",self.num)
            self.drop2.configure(state="disabled")
            
    def change_pic1(self): 
        if(self.num==1):
            self.check1.configure(image=photo)
            self.num+=1
            self.deportedCheck.set("No")
            print("num",self.num)
            self.drop2.configure(state="disabled")
        else:
            self.check1.configure(image=photo1)
            self.num-=1
            self.deportedCheck.set("Yes")
            print("num",self.num)
            self.drop2.configure(state="readonly")

    def radiobutt0(self):        
        if(self.num1[0]==1):
            self.radio1.configure(image=photo2)
            self.num1[0]-=1
        else:
            self.radio1.configure(image=photo3)
            self.num1[0]+=1
     
    def radiobutt1(self):
        if(self.num1[1]==1):
            self.radio2.configure(image=photo2)
            self.num1[1]-=1
        else:
            self.radio2.configure(image=photo3)
            self.num1[1]+=1
      
    def radiobutt2(self):
        if(self.num1[2]==1):
            self.radio3.configure(image=photo2)
            self.num1[2]-=1
        else:
            self.radio3.configure(image=photo3)
            self.num1[2]+=1
      
    def radiobutt3(self):
        if(self.num1[3]==1):
            self.radio4.configure(image=photo2)
            self.num1[3]-=1
        else:
            self.radio4.configure(image=photo3)
            self.num1[3]+=1
      
    def radiobutt4(self):
        if(self.num1[4]==1):
            self.radio5.configure(image=photo2)
            self.num1[4]-=1
        else:
            self.radio5.configure(image=photo3)
            self.num1[4]+=1
      
    def radiobutt5(self):
        if(self.num1[5]==1):
            self.radio6.configure(image=photo2)
            self.num1[5]-=1
        else:
            self.radio6.configure(image=photo3)
            self.num1[5]+=1
      
    def radiobutt6(self):
        if(self.num1[6]==1):
            self.radio7.configure(image=photo2)
            self.num1[6]-=1
        else:
            self.radio7.configure(image=photo3)
            self.num1[6]+=1
    
    def radiobutt7(self):
        if(self.num1[7]==1):
            self.radio8.configure(image=photo2)
            self.num1[7]-=1
        else:
            self.radio8.configure(image=photo3)
            self.num1[7]+=1
      
    def radiobutt8(self):
        if(self.num1[8]==1):
            self.radio9.configure(image=photo2)
            self.num1[8]-=1
        else:
            self.radio9.configure(image=photo3)
            self.num1[8]+=1
      
    def radiobutt9(self):
        if(self.num1[9]==1):
            self.radio10.configure(image=photo2)
            self.num1[9]-=1
        else:
            self.radio10.configure(image=photo3)
            self.num1[9]+=1
      
    def radiobutt10(self):
        if(self.num1[10]==1):
            self.radio11.configure(image=photo2)
            self.num1[10]-=1
        else:
            self.radio11.configure(image=photo3)
            self.num1[10]+=1
      
    def radiobutt11(self):
        if(self.num1[11]==1):
            self.radio12.configure(image=photo2)
            self.num1[11]-=1
        else:
            self.radio12.configure(image=photo3)
            self.num1[11]+=1
      
    def radiobutt12(self):
        if(self.num1[12]==1):
            self.radio13.configure(image=photo2)
            self.num1[12]-=1
        else:
            self.radio13.configure(image=photo3)
            self.num1[12]+=1
      
    def radiobutt13(self):
        if(self.num1[13]==1):
            self.radio14.configure(image=photo2)
            self.num1[13]-=1
        else:
            self.radio14.configure(image=photo3)
            self.num1[13]+=1

    def radiobutt14(self):
        if(self.num1[14]==1):
            self.radio15.configure(image=photo2)
            self.num1[14]-=1
        else:
            self.radio15.configure(image=photo3)
            self.num1[14]+=1
            
    def radiobutt15(self):
        if(self.num1[15]==1):
            self.radio16.configure(image=photo2)
            self.num1[15]-=1
        else:
            self.radio16.configure(image=photo3)
            self.num1[15]+=1
        
        
    def labelFun(self,new):
        
        label1 = ttk.Label(self.frame1, text="Port {}".format(self.index), font=("",20,'bold'), foreground='black', justify='left')
        label1.grid(column=0, row=0, padx=10, pady=10, sticky='W')
        label2 = ttk.Label(self.frame1, text="Label", font=15, foreground='black', justify='left')
        label2.grid(column=0, row=2, padx=10, pady=10, sticky='W')
        label3 = ttk.Label(self.frame1, text="Priority", font=15, foreground='black', justify='left')
        label3.grid(column=0, row=3, padx=10, pady=10, sticky='W')
        label4 = ttk.Label(self.frame1, text="Deported", font=15, foreground='black', justify='left')
        label4.grid(column=0, row=4, padx=10, pady=10, sticky='W')
        label5 = ttk.Label(self.frame1, text="Deported Pair", font=15, foreground='black', justify='left')
        label5.grid(column=0, row=5, padx=10, pady=10, sticky='W')
        label6 = ttk.Label(self.frame2, text="Call Restriction", font=15, foreground='black', justify='left')
        label6.grid(column=0, row=0, padx=10, pady=10, sticky='W')
        if(self.index<9):
            label7 = ttk.Label(self.frame1, text="Group 1 Dial 9", font=15, foreground='black', justify='left')
            label7.grid(column=5, row=2, padx=15, pady=10, sticky='W')
        else:
            label8 = ttk.Label(self.frame1, text="Group 2 Dial 9", font=15, foreground='black', justify='left')
            label8.grid(column=5, row=2, padx=15, pady=10, sticky='W')
        #-------------------------------------------------------------------------------------------------------------------------------
        label9 = ttk.Label(self.frame2, text="1", font=15, foreground='black', justify='center')
        label9.grid(column=1, row=1, padx=10, pady=10, sticky='W')
        label10 = ttk.Label(self.frame2, text="2", font=15, foreground='black', justify='center')
        label10.grid(column=2, row=1, padx=10, pady=10, sticky='W')
        label11 = ttk.Label(self.frame2, text="3", font=15, foreground='black', justify='center')
        label11.grid(column=3, row=1, padx=10, pady=10, sticky='W')
        label12 = ttk.Label(self.frame2, text="4", font=15, foreground='black', justify='center')
        label12.grid(column=4, row=1, padx=10, pady=10, sticky='W')
        label13 = ttk.Label(self.frame2, text="5", font=15, foreground='black', justify='center')
        label13.grid(column=5, row=1, padx=10, pady=10, sticky='W')
        label14 = ttk.Label(self.frame2, text="6", font=15, foreground='black', justify='center')
        label14.grid(column=6, row=1, padx=10, pady=10, sticky='W')
        label15 = ttk.Label(self.frame2, text="7", font=15, foreground='black', justify='center')
        label15.grid(column=7, row=1, padx=10, pady=10, sticky='W')
        label16 = ttk.Label(self.frame2, text="8", font=15, foreground='black', justify='center')
        label16.grid(column=8, row=1, padx=10, pady=10, sticky='W')
        label17 = ttk.Label(self.frame2, text="9", font=15, foreground='black', justify='center')
        label17.grid(column=9, row=1, padx=10, pady=10, sticky='W')
        label18 = ttk.Label(self.frame2, text="10", font=15, foreground='black', justify='center')
        label18.grid(column=10, row=1, padx=10, pady=10, sticky='W')
        label19 = ttk.Label(self.frame2, text="11", font=15, foreground='black', justify='center')
        label19.grid(column=11, row=1, padx=10, pady=10, sticky='W')
        label20 = ttk.Label(self.frame2, text="12", font=15, foreground='black', justify='center')
        label20.grid(column=12, row=1, padx=10, pady=10, sticky='W')
        label21 = ttk.Label(self.frame2, text="13", font=15, foreground='black', justify='center')
        label21.grid(column=13, row=1, padx=10, pady=10, sticky='W')
        label22 = ttk.Label(self.frame2, text="14", font=15, foreground='black', justify='center')
        label22.grid(column=14, row=1, padx=10, pady=10, sticky='W')
        label23 = ttk.Label(self.frame2, text="15", font=15, foreground='black', justify='center')
        label23.grid(column=15, row=1, padx=10, pady=10, sticky='W')
        label24 = ttk.Label(self.frame2, text="16", font=15, foreground='black', justify='center')
        label24.grid(column=16, row=1, padx=10, pady=10, sticky='W')
        
    
    def dropdownFun(self,new):
        label = ttk.Label(new, text="")
        label.grid(column=0, row=0, padx=10, pady=10, sticky='W')
        drop1 = ttk.Combobox(self.frame1, state="readonly", values=pri_options, textvariable=self.priority)
        drop1.grid(column=1,row=3, padx=10, pady=10)
        drop1.bind("<<ComboboxSelected>>",lambda e: label.focus())
        if(self.tF=="No"):
            self.drop2 = ttk.Combobox(self.frame1, state="disabled", values=options, textvariable=self.deportedPair)
            self.drop2.grid(column=1,row=5, padx=10, pady=10)
            self.drop2.bind("<<ComboboxSelected>>",lambda e: label.focus())
        else:
            self.drop2 = ttk.Combobox(self.frame1, state="readonly", values=options, textvariable=self.deportedPair)
            self.drop2.grid(column=1,row=5, padx=10, pady=10)
            self.drop2.bind("<<ComboboxSelected>>",lambda e: label.focus())
        if(self.index<9):
            if(self.dial9Var=='Yes'):
                self.dial91TF=tk.Button(self.frame1, activebackground='gray30', background='gray30', command=self.dial9Fun, image=photo1, height=21, width=21, relief="groove", textvariable=self.dial91)
                self.dial91TF.grid(column=6,row=2, padx=5, pady=5)
            else:
                self.dial91TF=tk.Button(self.frame1, activebackground='gray30', background='gray30', command=self.dial9Fun, image=photo, height=21, width=21, relief="groove", textvariable=self.dial91)
                self.dial91TF.grid(column=6,row=2, padx=5, pady=5)
            self.drop3 = ttk.Combobox(self.frame1, state="readonly", values=group1_options, textvariable=self.groupOption1)
            self.drop3.grid(column=7,row=2, padx=10, pady=10)
            self.drop3.bind("<<ComboboxSelected>>",lambda e: label.focus())
        else:
            if(self.dial9Var=='Yes'):
                self.dial91TF=tk.Button(self.frame1, activebackground='gray30', background='gray30', command=self.dial9Fun, image=photo1, height=21, width=21, relief="groove", textvariable=self.dial92)
                self.dial91TF.grid(column=6,row=2, padx=10, pady=10)
            else:
                self.dial91TF=tk.Button(self.frame1, activebackground='gray30', background='gray30', command=self.dial9Fun, image=photo, height=21, width=21, relief="groove", textvariable=self.dial92)
                self.dial91TF.grid(column=6,row=2, padx=5, pady=5)
            self.drop3 = ttk.Combobox(self.frame1, state="readonly", values=group2_options, textvariable=self.groupOption2)
            self.drop3.grid(column=7,row=2, padx=10, pady=10)
            self.drop3.bind("<<ComboboxSelected>>",lambda e: label.focus())
        if(self.dial9Var=='No'):
            self.drop3.configure(state="disabled")
    
    def entryFun(self,new):
        entry1 = tk.Entry(self.frame1, textvariable=self.labelEntry, font=("",12,""), width=22, relief="solid")
        entry1.grid(column=1,row=2, padx=10, pady=10)
    
    def func(self,event):
        print("You hit return.")
        self.submit()
    
    
    def buttonFun(self,new):
        sub_btn=tk.Button(new, text = 'Submit', font=("",10,"bold"), width=15, command = self.submit)
        sub_btn.grid(column=0,row=2, padx=10, pady=15, sticky='E')
        new.bind('<Return>', self.func)
    
    def checkFun(self,new, var=0):
        if(var==0):
            self.check1=tk.Button(self.frame1, activebackground='gray30', background='gray30', command=self.change_pic, image=photo, height=21, width=21, relief="groove", textvariable=self.deportedCheck)
            self.check1.grid(column=1,row=4, padx=7, pady=7)
        else:
            self.check1=tk.Button(self.frame1, activebackground='gray30', background='gray30', command=self.change_pic1, image=photo1, height=21, width=21, relief="groove", textvariable=self.deportedCheck)
            self.check1.grid(column=1,row=4, padx=7, pady=7)
        
    def radioFun(self,new):
        if(self.num1[0]==1):
            self.radio1=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt0, image=photo3, height=22, width=22)
            self.radio1.grid(column=1, row=0, padx=10, pady=10, sticky='W')  
        else:
            self.radio1=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt0, image=photo2, height=22, width=22)
            self.radio1.grid(column=1, row=0, padx=10, pady=10, sticky='W')    
        
        if(self.num1[1]==1):
            self.radio2=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt1, image=photo3, height=22, width=22)
            self.radio2.grid(column=2, row=0, padx=10, pady=10, sticky='W')       
        else:
            self.radio2=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt1, image=photo2, height=22, width=22)
            self.radio2.grid(column=2, row=0, padx=10, pady=10, sticky='W')     
        
        if(self.num1[2]==1):
            self.radio3=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt2, image=photo3, height=22, width=22)
            self.radio3.grid(column=3, row=0, padx=10, pady=10, sticky='W')    
        else:
            self.radio3=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt2, image=photo2, height=22, width=22)
            self.radio3.grid(column=3, row=0, padx=10, pady=10, sticky='W')   
        
        if(self.num1[3]==1):
            self.radio4=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt3, image=photo3, height=22, width=22)
            self.radio4.grid(column=4, row=0, padx=10, pady=10, sticky='W')        
        else:
            self.radio4=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt3, image=photo2, height=22, width=22)
            self.radio4.grid(column=4, row=0, padx=10, pady=10, sticky='W')       
            
        if(self.num1[4]==1):
            self.radio5=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt4, image=photo3, height=22, width=22)
            self.radio5.grid(column=5, row=0, padx=10, pady=10, sticky='W')        
        else:
            self.radio5=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt4, image=photo2, height=22, width=22)
            self.radio5.grid(column=5, row=0, padx=10, pady=10, sticky='W')       
        
        if(self.num1[5]==1):
            self.radio6=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt5, image=photo3, height=22, width=22)
            self.radio6.grid(column=6, row=0, padx=10, pady=10, sticky='W')       
        else:
            self.radio6=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt5, image=photo2, height=22, width=22)
            self.radio6.grid(column=6, row=0, padx=10, pady=10, sticky='W')        
        
        if(self.num1[6]==1):
            self.radio7=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt6, image=photo3, height=22, width=22)
            self.radio7.grid(column=7, row=0, padx=10, pady=10, sticky='W')        
        else:
            self.radio7=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt6, image=photo2, height=22, width=22)
            self.radio7.grid(column=7, row=0, padx=10, pady=10, sticky='W') 
            
        if(self.num1[7]==1):
            self.radio8=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt7, image=photo3, height=22, width=22)
            self.radio8.grid(column=8, row=0, padx=10, pady=10, sticky='W')        
        else:
            self.radio8=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt7, image=photo2, height=22, width=22)
            self.radio8.grid(column=8, row=0, padx=10, pady=10, sticky='W')       
            
        if(self.num1[8]==1):
            self.radio9=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt8, image=photo3, height=22, width=22)
            self.radio9.grid(column=9, row=0, padx=10, pady=10, sticky='W')     
        else:
            self.radio9=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt8, image=photo2, height=22, width=22)
            self.radio9.grid(column=9, row=0, padx=10, pady=10, sticky='W')     
        
        if(self.num1[9]==1):
            self.radio10=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt9, image=photo3, height=22, width=22)
            self.radio10.grid(column=10, row=0, padx=10, pady=10, sticky='W')        
        else:
            self.radio10=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt9, image=photo2, height=22, width=22)
            self.radio10.grid(column=10, row=0, padx=10, pady=10, sticky='W')        
        
        if(self.num1[10]==1):
            self.radio11=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt10, image=photo3, height=22, width=22)
            self.radio11.grid(column=11, row=0, padx=10, pady=10, sticky='W')        
        else:
            self.radio11=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt10, image=photo2, height=22, width=22)
            self.radio11.grid(column=11, row=0, padx=10, pady=10, sticky='W')        
            
        if(self.num1[11]==1):
            self.radio12=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt11, image=photo3, height=22, width=22)
            self.radio12.grid(column=12, row=0, padx=10, pady=10, sticky='W')  
        else:
            self.radio12=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt11, image=photo2, height=22, width=22)
            self.radio12.grid(column=12, row=0, padx=10, pady=10, sticky='W') 
        
        if(self.num1[12]==1):
            self.radio13=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt12, image=photo3, height=22, width=22)
            self.radio13.grid(column=13, row=0, padx=10, pady=10, sticky='W') 
        else:
            self.radio13=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt12, image=photo2, height=22, width=22)
            self.radio13.grid(column=13, row=0, padx=10, pady=10, sticky='W')  
        
        if(self.num1[13]==1):
            self.radio14=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt13, image=photo3, height=22, width=22)
            self.radio14.grid(column=14, row=0, padx=10, pady=10, sticky='W')      
        else:
            self.radio14=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt13, image=photo2, height=22, width=22)
            self.radio14.grid(column=14, row=0, padx=10, pady=10, sticky='W')        
        
        if(self.num1[14]==1):
            self.radio15=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt14, image=photo3, height=22, width=22)
            self.radio15.grid(column=15, row=0, padx=10, pady=10, sticky='W')
        else:
            self.radio15=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt14, image=photo2, height=22, width=22)
            self.radio15.grid(column=15, row=0, padx=10, pady=10, sticky='W')
        
        if(self.num1[15]==1):
            self.radio16=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt15, image=photo3, height=22, width=22)
            self.radio16.grid(column=16, row=0, padx=10, pady=10, sticky='W')
        else:
            self.radio16=tk.Button(self.frame2, activebackground='black', background='black', borderwidth=0, command=self.radiobutt15, image=photo2, height=22, width=22)
            self.radio16.grid(column=16, row=0, padx=10, pady=10, sticky='W')

rt = RootData(root)
rootdataobj = rt
rt.loadData(root)



######################################################################--Menu--################################################################

m = Menu(root)
root.config(menu=m)
file_menu = Menu(m, tearoff=False)
m.add_cascade(label="Menu", menu=file_menu)
file_menu.add_command(label="Open from file", command=open_file1)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As", command=save_as_file)


CMD_SWITCHER = {0: No_Action, 1: Write_CMD, 2: Read_CMD, 3: Password_change}

root.mainloop()