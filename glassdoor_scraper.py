from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium import webdriver
import time
from datetime import datetime
import pandas as pd
import pprint
from tabulate import tabulate
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

def search_keyword_on_google(keyword, num_jobs, verbose, chromedriver_path, sleep_time):
  #Initializing the webdriver
  options = webdriver.ChromeOptions()
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  #Uncomment the line below if you'd like to scrape without a new Chrome window every time.
  #options.add_argument('headless')
  
  # #Change the path to where chromedriver is in your home folder.
  driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
  
  # driver.set_window_size(1120, 1000)

  # # access the url via chrome driver
  driver.get('https://www.google.com/')
  driver.find_element_by_xpath("/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input").send_keys(keyword)
  driver.find_element_by_xpath("/html/body/div[1]/div[3]/form/div[1]/div[1]/div[3]/center/input[1]").click()
  founds = driver.find_elements_by_class_name("tF2Cxc")
  
  ls = []
  for i in range(len(founds)):
      try:
          title = founds[i].find_element_by_xpath(f'//*[@id="rso"]/div[{i+1}]/div/div/div[1]/a/h3').text
          link = founds[i].find_element_by_xpath(f'//*[@id="rso"]/div[{i+1}]/div/div/div[1]/a/div/cite').text
          try:
              sample_content = founds[i].find_element_by_xpath(f'//*[@id="rso"]/div[{i+1}]/div/div/div[2]/div').text
          except NoSuchElementException:
              sample_content = founds[i].find_element_by_xpath(f'//*[@id="rso"]/div[{i+1}]/div/div/div[2]/div[1]').text
      except NoSuchElementException as e:
          pprint.pprint(e)
          pass
      
      tmp = {
          'title': title,
          'link': link,
          'sample_content': sample_content,
      }
      
      ls.append(tmp)
  
  df = pd.DataFrame(ls)
  
  df.to_csv('sample_df.csv')
  
def contain_currency(text):
  currency = ['¥','$', '€', '£', 'VND']
  return any(c in text for c in currency)

def closeSignUpPopUp(driver):
  driver.find_element(by=By.CSS_SELECTOR, value='[alt="Close"]').click()

def logTextToFile(path, mode, text):
  if path:
    with open(path, mode, encoding='utf-8') as f:
      f.write(text)
      
def get_jobs(*, keyword, num_jobs, chromedriver_path, sleep_time, save_csv_path=None, save_rawdata_path=None):
    
  """Gathers jobs as a dataframe, scraped from Glassdoor"""
  
  #Initializing the webdriver
  options = webdriver.ChromeOptions()
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  
  #Change the path to where chromedriver is in your home folder.
  driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
  driver.set_window_size(1120, 1000)

  url = f'https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keyword}'
  
  # access the url via chrome driver
  driver.get(url)
  
  job_ls = []
  
  if save_rawdata_path:
    with open(save_rawdata_path, "a", encoding="utf8") as f:
      f.write(f"\n\n##### Logtime: {datetime.now()}\n")
            
  while len(job_ls) < num_jobs:
    job_cards = driver.find_elements(by=By.CSS_SELECTOR, value ="#MainCol > div:nth-child(1) > ul > *")
    
    for card in job_cards:
      if len(job_ls) < num_jobs:
        print(f'Progress: {len(job_ls)+1} / {num_jobs}')
        
        logTextToFile(save_rawdata_path, 'a', card.text)
            
        job_info = card.text.split('\n')

        try:
          rating = float(job_info[0])
        except ValueError:
          rating = -1
          pass
        else:
          job_info = job_info[1:]
        
        company = job_info[0]
        
        job_title = job_info[1]
        
        if contain_currency(job_info[2]):
          where = ''
          salary = job_info[2]
        else:
          where = job_info[2]
          salary = job_info[3] if contain_currency(job_info[3]) else -1
        
        posted_day = job_info[-1] + ' ago from ' + str(datetime.now())
        
        try:
          card.click()
        except ElementClickInterceptedException:
          closeSignUpPopUp(driver)
          card.click()
          
        time.sleep(sleep_time)
        
        extracted_job_info = {}
        
        try:
          job_type = driver.find_element(by=By.CSS_SELECTOR, value='#JDCol > div > article > div > div:nth-child(1) > div > div > div.css-1uoh7o7.epgue5a2 > div:nth-child(2) > div:nth-child(2)')
        except:
          pass
        else:
          logTextToFile(save_rawdata_path, 'a', job_type.text)
          extracted_job_info['Job_Type'] = job_type.text.split(':')[1]
        
        try:
          company_overview = driver.find_elements(by=By.CSS_SELECTOR, value='#EmpBasicInfo > div:nth-child(1) > div > *')
        except:
          pass
        else:
          for e in company_overview:
            logTextToFile(save_rawdata_path, 'a', e.text)
            company_attribute = e.text.split('\n')
            extracted_job_info[company_attribute[0]] = company_attribute[1]

        try:
          driver.find_element(by=By.CSS_SELECTOR, value='#JobDescriptionContainer > div.css-t3xrds.e856ufb5').click()
          job_desc = driver.find_element(by=By.ID, value='JobDescriptionContainer')
        except:
          pass
        else:
          logTextToFile(save_rawdata_path, 'a', job_desc.text)
          extracted_job_info['Job Description'] = job_desc.text
             
        extracted_job_info.update({
          'Job Title': job_title,
          'Company Name': company,
          'Rating': rating,
          'Workplace': where,
          'Salary': salary,
          'Posted Day': posted_day,
        })

        job_ls.append(extracted_job_info)
        
        logTextToFile(save_rawdata_path, 'a', '\n\n')
    try:
      driver.find_element(by=By.CSS_SELECTOR, value='#FooterPageNav > div > ul > li.css-114lpwu.e1gri00l4 > a > span').click()
    except ElementClickInterceptedException:
      closeSignUpPopUp(driver)
      
  return pd.DataFrame(job_ls).to_csv(save_csv_path) if save_csv_path else pd.DataFrame(job_ls)