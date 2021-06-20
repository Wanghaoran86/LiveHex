#R2=8M[0xD687730]
#R2=8M[R2+0x160]
#R2=8M[R2+0x10]
#R2=8M[R2+0x20+8*(n-1)]
#R2=R2+0x40
#M[R2] = 0x|xxxx 0410 xxxx

#[[[[main+D687730]+160]+10]+20]+40

import socket
import time
import binascii

def send_command(s, content):
    content += '\r\n' #important for the parser on the switch side
    s.sendall(content.encode())

def connect(nip,port=6000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((nip, port))
    return s

def get_8(s, cmd):
    send_command(s, cmd)
    time.sleep(0.1) #give time to answer
    return s.recv(8 * 2 + 1)

def get_version(s):
    r = get_8(s, f"getVersion")
    print(r)

def get_title_id(s):
    r = get_8(s, f"getTitleID")
    print(r)

def get_build_id(s):
    r = get_8(s, f"getBuildID")
    print(r)

def set_addr(s,addr,data):
    ed = data.to_bytes(2,'little')
    st = binascii.hexlify(ed).decode()
    send_command(s, f"pokeAbsolute {hex(addr)} 0x{st}") # hex already has 0x prefix

def get_1st_offset(s,offset1 = 'D687730'):
    lengh = 5
    send_command(s, f"peekMain 0x{offset1} {lengh}")
    time.sleep(0.5) #give time to answer
    ofs = ''
    #return s.recv(11)
    for i in range(lengh):
        ofs = s.recv(2).decode() + ofs
    s.recv(2)
    #return ofs

    a = ofs
    if int(a, 16) == 0:
        return a
    
    #[[[[main+DB446D0]+58]+18]
    n=get_next_addr(s,a,0x58)
    n=get_next_addr(s,n,0x18)

    return n

def get_next_addr(s,offset_1st, offset_n, lengh=5):
    a=int(offset_1st,16) + offset_n
    send_command(s, f"peekAbsolute {hex(a)} {lengh}")
    time.sleep(0.1) #give time to answer
    ofs = ''
    for i in range(lengh):
        ofs = s.recv(2).decode() + ofs
    s.recv(2)
    return ofs

def get_item(s,n,bag_num = 1):
    a=int(n, 16)
    if a == 0:
        return -1

    if bag_num < 1:
        bag_num = 1
    if bag_num > 1200:
        bag_num = 1200
    
    #+0x20 + offset
    n=get_next_addr(s,n,0x20+8*(bag_num-1)) # 
    # num ~ 1-1200

    #+0x40
    item=get_next_addr(s,n,0x40,6)

    item_id = item[8:]
    item_state = item[4:8] # always 0410?
    item_cont = item[:4]

    return (int(item_id, 16), int(item_cont, 16),  item_state, int(n,16) + 0x40)

def set_item(s,n,bag_num,itemid = -1,cont = -1):
    item = get_item(s,n,bag_num)
    if item == -1:
        return
    if item[2] == '0410' or item[2] == '0400':
        set_addr(s,item[3]+2, 1040) #'0410'

        if itemid != -1:
            set_addr(s,item[3], itemid)
        if cont != -1:
            set_addr(s,item[3]+4, cont)
    else:
        print('cannt write item')
        return

s=connect("192.168.1.26")
#send_command(s, f"pointerAll 0xD9674B8 0x60 0x10")
#pointer
#pointerAll
#pointerPeek/Poke
get_version(s)
get_title_id(s)
get_build_id(s)
#idx = 99
#item = get_item(s,n, idx)
#set_item(s,n, idx, 172,990)
#item = get_item(s,n, idx)
#print(item)