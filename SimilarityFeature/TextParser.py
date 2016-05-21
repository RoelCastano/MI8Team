import os, sys,stat
import re
import base64
   
def remove_braces(input_file,output_file):
    with open(input_file,'r',encoding='utf-8') as input:
        textpart = ""
        with open(output_file,'w',encoding='utf-8') as out :
            for line in input :
                textpart = (textpart+line).replace('\n', '')
                (first,last) = find_first_braces(textpart)

                # find {{...}}
                while first != -1 and last!=-1 :
                    out.write(textpart[0:first])
                    if last+1<len(textpart) :
                        textpart = textpart[last+1:len(textpart)]
                    else :
                        textpart = ""
                    (first,last) = find_first_braces(textpart)
            out.write(textpart)                    
        out.close()
    input.close()

def find_first_braces(text):

    opening_brace = text.find("{{")
    closing_brace = text.find("}}")
    first = opening_brace
    last = -1
    
    # if opening_brace==-1 or closing_brace==-1:
        # return(-1,-1)

    #else :
    stack = []
    while(closing_brace!=-1) :            
        # found opening braces {{ : push
        if opening_brace<closing_brace and opening_brace != -1:
            stack.append(opening_brace)
            if closing_brace !=-1:
                opening_brace=text.find("{{",opening_brace+2,len(text))
            
        # found closing braces    }} : pop       
        elif closing_brace<opening_brace or opening_brace==-1:            
            if stack :
                stack.pop()                
                if closing_brace !=-1:
                    last = closing_brace+1
                closing_brace = text.find("}}",closing_brace+2,len(text))
            
        # check if stack is empty
        if not stack :
            return (first,last)
    
    # return (-1,-1) if stack is not empty     
    if stack :
        last = -1

    return (first,last)                   

def clear_text(input_file,output_file) :
    remove_braces(input_file,"tmp_file")
    with open("tmp_file",'r',encoding='utf-8') as input :
        newtext = input.read()
    input.close()
    # exclude end of article (from "see also section to the end"        
    index = newtext.find("==See also==")
    if index != -1 :
        newtext = newtext[0:index]
    exclude_regex = [r"<[^>]*>*>[^>]*<\/[^>]*>", r"<[^>]*>",r"\[\[File:.*\]\]",r"\{\|\s?class=[^\}]*\|\}",r"\*\s\[http\:\/\/.*",r"\"\[http\:\/\/[^\]]*\]\"",r"\[\[Category[^\]]*\]]"]
    with open(output_file,'w',encoding='utf-8') as out :    
        for regex in exclude_regex:
            newtext = re.sub(regex,"",newtext)
        out.write(newtext)
    out.close()
    
    os.remove("tmp_file")
    
def parser(src_files_dir):

    # creating de parsed files directory
    parsed_files_dir = os.path.join(src_files_dir,"parsed_files")
    if not os.path.exists(parsed_files_dir):
        os.makedirs(parsed_files_dir)

    # parsing all files
    print("Parsing text files ...")
    src_files = [f for f in os.listdir(src_files_dir) if os.path.isfile(os.path.join(src_files_dir, f))]
    for filename in src_files:
        parse_file(filename,src_files_dir)
    return parsed_files_dir

def parse_file(filename,src_files_dir):
    # creating de parsed files directory
    parsed_files_dir = os.path.join(src_files_dir,"parsed_files")
    if not os.path.exists(parsed_files_dir):
        os.makedirs(parsed_files_dir)

    # parsing file            
    if not os.path.exists(os.path.join(src_files_dir,filename)): # the input file name is encoded (b64)
        filename = base64.b64encode(filename.encode('utf-8')).decode('utf-8')
    
    input_file = os.path.join(src_files_dir,filename)  
    output_file = os.path.join(parsed_files_dir,filename)    
    
    if os.path.exists(input_file):
        if not os.path.exists(output_file) : # don't parse if the file already exist
            clear_text(input_file,output_file)
            print(filename)
    else :
        print(os.path.join(src_files_dir,filename),"not found")
        
    return output_file

def main():
    file = sys.argv[1]
    # remove_braces(file,"hello")
    # print(find_first_braces(file))
    parser(file)
    
if __name__ == "__main__":
    main()