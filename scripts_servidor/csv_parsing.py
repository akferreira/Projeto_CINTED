import csv


with open("/home/arthur/Documents/cinted/compar/choices.csv") as choices:
    choices_dict = csv.DictReader(choices, delimiter = ';')
    
    
    with open("/home/arthur/Documents/cinted/compar/acessed_general.csv",'w+') as accessed:
        accessed.write("type;resourceid;userid;timeunix\n")
        for access in choices_dict:
            accessed.write(f"choice;{access['choiceid']};{access['userid']};{access['timeunix']}\n")

with open("/home/arthur/Documents/cinted/compar/forums.csv") as forums:
    forums_dict = csv.DictReader(forums, delimiter = ';')
    
    with open("/home/arthur/Documents/cinted/compar/acessed_general.csv",'a+') as accessed:
        for access in forums_dict:
            accessed.write(f"forum;{access['forumid']};{access['userid']};{access['timeunix']}\n")

            
            
with open("/home/arthur/Documents/cinted/compar/chats.csv") as chats:
    chats_dict = csv.DictReader(chats, delimiter = ';')
    
    with open("/home/arthur/Documents/cinted/compar/acessed_general.csv",'a+') as accessed:
        for access in chats_dict:
            accessed.write(f"chat;{access['chatid']};{access['userid']};{access['timeunix']}\n")
            
with open("/home/arthur/Documents/cinted/compar/folders.csv") as folders:
    folders_dict = csv.DictReader(folders, delimiter = ';')
    
    with open("/home/arthur/Documents/cinted/compar/acessed_general.csv",'a+') as accessed:
        for access in folders_dict:
            accessed.write(f"folder;{access['folderid']};{access['userid']};{access['timeunix']}\n")


#with open("/home/arthur/Documents/cinted/compar/files.csv") as files:
    #files_dict = csv.DictReader(files, delimiter = ';')
    
    #with open("/home/arthur/Documents/cinted/compar/acessed_general.csv",'a+') as accessed:
        #for access in files_dict:
            #accessed.write(f"file;{access['fileid']};{access['userid']};{access['timeunix']}\n")
