# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 04:28:09 2021

@author: HuynhDat
"""
# standard imports
from datetime import datetime

# third-party imports
import pandas as pd

# main implementation
data = pd.read_csv("glassdoor_jobs.csv", index_col=0)

data = data[data['Salary'] != '-1']
salary = data['Salary'].apply(lambda x: x.split('(')[0])
salary_minus_Kd = salary.apply(lambda x: x.replace('K', '').replace('$', ''))

data['hourly'] = data['Salary'].apply(lambda x: 1 if 'per hour' in x.lower() else 0)

salary_minus_hr = salary_minus_Kd.apply(lambda x: x.lower().replace('per hour', ''))

data['min_salary'] = salary_minus_hr.apply(lambda x: int(x.split('-')[0]) if '-' in x else int(x))
data['max_salary'] = salary_minus_hr.apply(lambda x: int(x.split('-')[1]) if '-' in x else int(x))
data['avg_salary'] = (data["min_salary"] + data['max_salary']) / 2

data['job_state'] = data['Workplace'].apply(lambda x: x.split()[-1] if x.lower() != 'remote' else None)
data['job_state'].value_counts()

data['age'] = data['Founded'].apply(lambda x: datetime.now().year - x if x > 0 else x)

data['python_yn'] = data['Job Description'].apply(lambda x: 1 if 'python' in x.lower() else 0)
data['python_yn'].value_counts()

data['r_yn'] = data['Job Description'].apply(lambda x: 1 if 'rstudio' in x.lower() or 'r-studio' in x.lower() or 'r studio' in x.lower() else 0)
data['r_yn'].value_counts()

data['aws_yn'] = data['Job Description'].apply(lambda x: 1 if 'aws' in x.lower() else 0)
data['aws_yn'].value_counts()

data['spark_yn'] = data['Job Description'].apply(lambda x: 1 if 'spark' in x.lower() else 0)
data['spark_yn'].value_counts()

data.columns

data.to_csv("salary_data_cleaned.csv")
