from flask import Flask, render_template, request, send_file, url_for, make_response, send_from_directory
from PyPDF2 import PdfFileWriter, PdfFileReader
from werkzeug.utils import secure_filename
import os
import shutil

app = Flask(__name__, static_folder='',static_url_path='')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/split', methods=['GET','POST']) 
def split():

    if request.method == 'POST':
        page_number_raw = str(request.form['page'])
        filename_raw = str(request.form['filename'])

        check1 = page_number_raw.split(",")
        check2 = filename_raw.split(",")

        if len(check1) != len(check2):
            return render_template('index.html',error_message="The number of pages to be split and filenames must be same")
        elif len(check2) != len(check1):
            return render_template('index.html',error_message="The number of pages to be split and filenames must be same")     
        else:
            #removing all the existing pdfs present from the last run
            for root,dirs,files in os.walk("web_folder/pdfs/"):
                for file in files:
                    os.remove("web_folder/pdfs/"+file)
            file = request.files['file']
        
            filename = secure_filename(file.filename)
            file.save(filename)
            pdfFileObj = open(file.filename, 'rb')


            l = page_number_raw.split(",")
            filename = filename_raw.split(",")

            #print(l,filename)

            original_pdf = PdfFileReader(pdfFileObj) # Reading the original pdf to be splitted
            totalpages = original_pdf.numPages
            last_split = l[-1]
            if "-" in last_split:
                s,e = map(int,last_split.split("-"))
            else:
                e = int(last_split)

            if totalpages < e: #checking if the user input of pages exceeds the pdf pages
                return render_template('index.html',error_message="The number of pages to split exceeds number of pages in pdf")
            else:
                start_page = 0
                filecount = 0

                for i in l:
                    if "-" in i:
                        start,end = map(int,i.split("-"))
                        pdf_writer = PdfFileWriter()
                        for j in range(start_page,start_page+end-start+1):
                            pdf_writer.addPage(original_pdf.getPage(j))
                            outputfilename = filename[filecount] + ".pdf"

                        with open("web_folder/pdfs/"+outputfilename, 'wb') as output_pdf:
                            pdf_writer.write(output_pdf)

                        print("Created Pdf :",outputfilename)
                        start_page = end-start+1

                        pdfoutput = open("web_folder/pdfs/"+outputfilename,'wb')
                        pdf_writer.write(pdfoutput)
                        pdfoutput.close()

                    else:
                        pdf_writer = PdfFileWriter()
                        pdf_writer.addPage(original_pdf.getPage(int(i)-1))
                        outputfilename = filename[filecount] + ".pdf"
                        
                        with open("web_folder/pdfs/"+outputfilename, 'wb') as output_pdf:
                            pdf_writer.write(output_pdf)

                        print("Created Pdf :",outputfilename)
                        start_page = i

                        pdfoutput = open("web_folder/pdfs/"+outputfilename,'wb')
                        pdf_writer.write(pdfoutput)
                        pdfoutput.close()
                        

                    filecount += 1
            
            print("removed old zip file")
            os.remove('web_folder/pdfs.zip') #removing the old pdfs.zip file
            
            #creating new zip file of folder pdfs
            shutil.make_archive('pdfs','zip','web_folder/pdfs')

            print("New zip created")
            #sending the new pdfs.zip folder created to the frontend (trigger download in the user machine)
            return send_file('pdfs.zip',mimetype='zip',as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
