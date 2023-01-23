import os
import re
import json
import ftfy
import spacy
import codecs
import requests
import calendar
import docx2txt
import pandas as pd
import win32com.client
from datetime import datetime
from dateutil import relativedelta
from unidecode import unidecode
from pyresparser import ResumeParser
from pdfminer.high_level import extract_text
from dateutil.relativedelta import relativedelta

storage_path = "C://Users/ChintalapudiTejaswin/Documents/sort_project/django_skill_matrix/django_project/skillblog/data/"

class ResumeAnalyzerMachine:
    def get_total_years_and_months(self,time_period):
        time_span_list = list()
        fmts=("%b%Y", "%B%Y", "%b %Y", "%B %Y", "%Y%b", "%Y%B")
        if time_period:
            time_span_list = list()
            for period in time_period:
                try:
                    period = datetime.strptime(period, "%b %Y").strftime("%b %Y")
                    time_span_list.append(period)
                except:
                    for fmt in fmts:
                        try:
                            period1 = datetime.strptime(period,fmt).strftime("%b %Y")
                        except ValueError:
                            continue
                    time_span_list.append(period1)
            
            for fmt in fmts:
                try:
                    time_span_list.sort(key = lambda date: datetime.strptime(date,fmt))
                    start_date = datetime.strptime(time_span_list[0],fmt)
                    end_date = datetime.strptime(time_span_list[-1],fmt)
                    delta = relativedelta(end_date, start_date)
                    return delta
                except ValueError:
                    continue
                    
    def parse_date(self,x, fmts=("%b%Y", "%B%Y", "%b %Y", "%B %Y", "%Y%b", "%Y%B")):
        """
            this function will parse the date depending on the date format 
            example: June2022, Apr2010, Apr 2010 
            Args: x (date format)
        """
        for fmt in fmts:
            try:
                return datetime.strptime(x, fmt)
            except ValueError:
                pass
        
    def get_employee_total_experience(self,text):
        """
            this function will extract the total experience of the Employee
            Args: text  (textual data of the employee resume)
        """
        months = "|".join(calendar.month_abbr[1:] + calendar.month_name[1:])
        #fr"(?i)((?:{months}) *\d{{4}}) *(?:-|–) *(present|(?:{months}) *\d{{4}})"
        pattern = fr"(?i)((?:{months}) *\d{{4}}) *(?:-|–) *(current|till date|present|(?:{months}) *\d{{4}})"
        total_experience = None
        time_period = list()
        for start, end in re.findall(pattern, text):
            if end.lower() == "present":
                today = datetime.today()
                end = f"{calendar.month_abbr[today.month]} {today.year}"
            elif end.lower() == "till date":
                today = datetime.today()
                end = f"{calendar.month_abbr[today.month]} {today.year}"
            elif end.lower() == "current":
                today = datetime.today()
                end = f"{calendar.month_abbr[today.month]} {today.year}"

            duration = relativedelta(self.parse_date(end), self.parse_date(start))

            if total_experience:
                total_experience += duration
            else: 
                total_experience = duration
                
            time_period.extend([str(start),str(end)])

        total_experience = self.get_total_years_and_months(time_period)
        
        if total_experience:
            return(f"{total_experience.years} years, {total_experience.months} months")
        else:
            return("couldn't parse text")

    def convert_list_to_string(self,data_list):
        # Convert the list to a string using str.format
        new_data_list = [word.capitalize() for word in data_list]
        data_str = "{}, "*int(len(new_data_list))
        result = data_str.format(*new_data_list)
        return result.strip(",")
            
    def extract_text_from_file(self,file_path):
        """
            depending the file extension type this function will classify the data 
            and extract text from the resumes
            Args: file_path  (resume file path)
        """
        file_extension = file_path.split(".")[-1]
        if file_extension == "pdf":
            text = extract_text(file_path)
            text = ftfy.fix_text(text).replace(u'\xa0', ' ').encode('utf-8')
            text = codecs.decode(text).replace("•"," ")
            return text
        elif file_extension == "docx":
            text = docx2txt.process(file_path)
            if text:
                text.replace('\t', ' ')
                text = ftfy.fix_text(text).replace(u'\xa0', ' ').encode('utf-8')
                text = codecs.decode(text).replace("•"," ")
            return text
        elif file_extension == "doc":
            app = win32com.client.Dispatch( 'Word.Application' )
            doc = app.Documents.Open( Directory )
            text = doc.Content.Text
            app.Quit()
            if text:
                text.replace('\t', ' ')
                text = ftfy.fix_text(text).replace(u'\xa0', ' ').encode('utf-8')
                text = codecs.decode(text).replace("•"," ")
            return text
        else:
            return None
        
    def extract_skillset(self,resume_text,skill_jsondata):
        """
            this function will tokenize the given data and extract the skills from the resume data.
            Args: resume_text     (textual resume data)
                    skill_jsondata  (jsondata file which include all the technical terms belonging to various skills)
        """
        tokens = []
        skillset = []
        skills = skill_jsondata['skills']
        nlp = spacy.load('en_core_web_sm')
        nlp_text = nlp(resume_text)

        for chunk in nlp_text.noun_chunks:
            if re.split(r'\s{2,}',chunk.text):
                text_spliter = re.split(r'\s{2,}',chunk.text)
                tokens.extend(text_spliter)
            elif re.split(r',',chunk.text):
                text_spliter = re.split(r',',chunk.text)
                tokens.extend(text_spliter)
            else:
                tokens.append(chunk.text)
        for token in tokens:
            if token in skills:
                skillset.append(token)
        return skillset

    def to_add_new_skill_to_json(self,new_skillset = [],remove_skillset = []):
        """
            this function will add the new cutting edge technology terms into the skillset
        """
        if new_skillset:
            with open(storage_path + "skills.json","r") as f:
                skill_jsondata = json.load(f)
            skill_jsondata['skills'].extend(new_skillset)
            skill_jsondata['skills'] = list(set(skill_jsondata['skills']))
            with open(storage_path + "skills.json","w") as f:
                skill_jsondata = json.dump(skill_jsondata,f)
            return True
        elif remove_skillset:
            with open(storage_path + "skills.json","r") as f:
                skill_jsondata = json.load(f)
            for item in remove_skillset:
                skill_jsondata['skills'].remove(item)
            with open(storage_path + "skills.json","w") as f:
                skill_jsondata = json.dump(skill_jsondata,f)
            return True
        else:
            return "provide the skills in list format"
        
        
    def start_machine(self,file_name):
        file_path = storage_path + file_name
        data_dict = dict()
        with open(storage_path + "skills.json","r") as f:
            skill_jsondata = json.load(f)
        resume_text = self.extract_text_from_file(file_path)
        if resume_text:
            skillset = self.extract_skillset(resume_text,skill_jsondata)
            total_experience = self.get_employee_total_experience(resume_text)
            data_dict['skillset'] = list(set(skillset))
            data_dict['total_experience'] = total_experience
            return data_dict
        else:
            return "resume text classification failed"