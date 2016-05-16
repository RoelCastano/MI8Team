import os, sys,stat
import re
   
def split_braces(text):
    unparsed_text = text
    res = []
    (first,last) = find_first_braces(text)
  
    while((first,last)!=(-1,-1)):
   
        res.append(unparsed_text[0:first])
        res.append(unparsed_text[last+1:len(unparsed_text)])
        
        unparsed_text = res.pop()

        (first,last) = find_first_braces(unparsed_text)
        
    res.append(unparsed_text)   
    return res

def find_first_braces(text):

    opening_brace = text.find("{{")
    closing_brace = text.find("}}")
    first = opening_brace
    last = closing_brace
    
    if opening_brace==-1 or closing_brace==-1 or closing_brace<opening_brace:
        return(-1,-1)

    else :
        stack = ["END"]    
        while(stack):
            # found opening braces {{ : push
            if opening_brace<closing_brace :
                stack.append(opening_brace)
                opening_brace=text.find("{{",opening_brace+2,len(text)-1)
            # found closing braces    }} : pop        
            if closing_brace<opening_brace or opening_brace==-1:            
                stack.pop()
                last = closing_brace+1
                closing_brace = text.find("}}",closing_brace+2,len(text)-1)

            # check if stack is empty
            p = stack.pop()
            if p != "END" :
                stack.append(p)
    return (first,last)            

def remove_braces(text):
    newtext=""
    paragraphs = split_braces(text)
    for p in paragraphs:
        newtext = newtext+p
    return newtext

def clear_text(text) :
    newtext = text
    exclude_regex = [r"<[^>]*>*>[^>]*<\/[^>]*>", r"<[^>]*>",r"\[\[File:.*\]\]",r"\{\{[^\}]*\}\}",r"\{\|\s?class=[^\}]*\|\}",r"\*\s\[http\:\/\/.*",r"\"\[http\:\/\/[^\]]*\]\"",r"\[\[Category[^\]]*\]]"]
    for regex in exclude_regex:
        newtext = re.sub(regex,"",newtext) 
    # exclude end of article (from "see also section to the end"        
    index = newtext.find("==See also==")
    if index != -1 :
        newtext = newtext[0:index]
    return newtext   
    
def parser(src_files_dir):

    # creating de parsed files directory
    parsed_files_dir = os.path.join(src_files_dir,"parsed_files")
    if not os.path.exists(parsed_files_dir):
        os.makedirs(parsed_files_dir)
    os.chmod(parsed_files_dir,stat.S_IRWXO)

    # parsing all files
    print("Parsing text files ...")
    src_files = os.listdir(src_files_dir)
    for filename in src_files:
    
        input = os.path.join(src_files_dir,filename)
        output = os.path.join(parsed_files_dir,filename)
        
        if os.path.isfile(input) :
            with open(input,'r',encoding="utf-8") as f:
                with open(output,'w',encoding="utf-8") as out:
                    text = f.read()
                    # clearing the text
                    print("Reading ",input)
                    text = remove_braces(text)
                    text = clear_text(text)
                    out.write(text)                                       
                out.close()
            f.close()
    
    return parsed_files_dir

def parse_file(filename,src_files_dir):
    # creating de parsed files directory
    parsed_files_dir = os.path.join(src_files_dir,"parsed_files")
    if not os.path.exists(parsed_files_dir):
        os.makedirs(parsed_files_dir)
    os.chmod(parsed_files_dir,stat.S_IRWXO)

    # parsing file
    output = os.path.join(parsed_files_dir,filename)
    input = os.path.join(src_files_dir,filename)    
    if os.path.isfile(input) :
        if not os.path.exists(output) : # don't parse if the file already exist
            with open(input,'r',encoding="utf-8") as f:
                with open(output,'w',encoding="utf-8") as out:
                    text = f.read()
                    # clearing the text
                    print("Reading ",input)
                    text = remove_braces(text)
                    text = clear_text(text)
                    out.write(text)                                       
                out.close()
            f.close()
            
    return output
    