# standard imports
import time
from datetime import datetime
import pprint

# third-party imports
import pandas as pd
from tabulate import tabulate
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException


def contain_currency(text):
  currency = ['¥','$', '€', '£', 'VND']
  return any(c in text for c in currency)

def closeSignUpPopUp(driver):
  driver.find_element(by=By.CSS_SELECTOR, value='[alt="Close"]').click()

def logTextToFile(path, mode, text):
  if path:
    with open(path, mode, encoding='utf-8') as f:
      f.write(text)

def wait_for(condition_func, max_wait_period: float = 10.0, args: tuple = ()):
    # refs: https://www.cloudbees.com/blog/get-selenium-to-wait-for-page-load
    
    start_time = time.time()
    while time.time() < start_time + max_wait_period:
        if condition_func(*args):
            return True
        else:
            time.sleep(.1)
    
    raise Exception(
        f'Timeout waiting for {condition_func.__name__}'
        )
        
def clickElementAndWaitForLoading(*, driver, click_find_by=None, click_find_value=None,
                                  click_element=None, checked_find_by, checked_find_value, 
                                  max_wait_period=10, click_exception_handler=None, 
                                  click_exception_handler_args: tuple = (),
                                  wait_method = 'elementHasGoneStale',
                                  usr_defined_wait_method = None,
                                  usr_defined_wait_method_args: tuple=()
                                  ):
    
    checked_element = driver.find_element(by=checked_find_by, value=checked_find_value)
    old_content = checked_element.text
    
    if not click_element:
        click_element = driver.find_element(by=click_find_by, value=click_find_value)
        
    try:
        click_element.click()
    except Exception as excpt:
        if not click_exception_handler:
            raise excpt
        elif click_exception_handler == 'pass':
            print("clickElementAndWaitForLoading captures a Click Exception" + str(excpt))
            pass
        else:
            print("clickElementAndWaitForLoading captures a Click Exception" + str(excpt))
            click_exception_handler(*click_exception_handler_args)
        
    def elementHasGoneStale(stale_checked_element):
        try:
            # poll the element with an arbitrary call
            t = stale_checked_element.text
            return False
        except StaleElementReferenceException:
            return True
    
    def contentChange(driver, old_content, checked_find_by, checked_find_value):
        ele = driver.find_element(by=checked_find_by, value=checked_find_value)
        try:
            new_content = ele.text
        except StaleElementReferenceException:
            return True
        
        return old_content != new_content
    
    if usr_defined_wait_method:
        wait_for(usr_defined_wait_method, max_wait_period, args=usr_defined_wait_method_args)
    elif wait_method == 'elementHasGoneStale':
        wait_for(elementHasGoneStale, max_wait_period, args=(checked_element, ))
    elif wait_method == 'contentChange':
        wait_for(contentChange, max_wait_period, args=(driver, old_content, checked_find_by, checked_find_value))

def finishCloseSignUpPopUp(driver):
    time.sleep(1)
    try:
        closeSignUpPopUp(driver)
    except:
        pass
    else:
        time.sleep(1)
    return True

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
    driver.get(url) # wait until the page is loaded.

    job_ls = []
    
    if save_rawdata_path:
        with open(save_rawdata_path, "a", encoding="utf8") as f:
            f.write(f"\n\n##### Logtime: {datetime.now()}\n")
            
    while len(job_ls) < num_jobs:
        # get job cards
        job_cards = driver.find_elements(
            by=By.CSS_SELECTOR, 
            value ="#MainCol > div:nth-child(1) > ul > *"
        )
    
        for card in job_cards:
            if len(job_ls) < num_jobs:
                print(f'Progress: {len(job_ls)+1} / {num_jobs}')
                
                start_time = datetime.now()
                
                extracted_job_info = {}
                
                logTextToFile(save_rawdata_path, 'a', card.text + '\n')
                
                try:
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
                except IndexError as e:
                    print("Capturing IndexError: " + str(e))
                    print(card.text)
                    continue # out the current for loop
                else:
                    extracted_job_info.update({
                      'Job Title': job_title,
                      'Company Name': company,
                      'Rating': rating,
                      'Workplace': where,
                      'Salary': salary,
                      'Posted Day': posted_day,
                    })

                if card != job_cards[0]:
                    clickElementAndWaitForLoading(
                        driver=driver, click_element=card,
                        checked_find_by=By.CSS_SELECTOR,
                        checked_find_value='#JDCol > div > article > div > div:nth-child(1) > div > div > div.css-vwxtm.evnfo7p1 > div.css-19txzrf.e14vl8nk0 > div.css-w04er4.e1tk4kwz6',
                        max_wait_period=10.0,
                        wait_method='contentChange',
                        usr_defined_wait_method=finishCloseSignUpPopUp if card == job_cards[1] else None,
                        usr_defined_wait_method_args=(driver, )
                    )
                
                try:
                    job_type = driver.find_element(by=By.CSS_SELECTOR, value='#JDCol > div > article > div > div:nth-child(1) > div > div > div.css-1uoh7o7.epgue5a2 > div:nth-child(2) > div:nth-child(2)')
                except:
                    pass
                else:
                    logTextToFile(save_rawdata_path, 'a', job_type.text + '\n')
                    extracted_job_info['Job Type'] = job_type.text.split(':')[1]

                try:
                    company_overview = driver.find_elements(by=By.CSS_SELECTOR, value='#EmpBasicInfo > div:nth-child(1) > div > *')
                except:
                    pass
                else:
                    for e in company_overview:
                        logTextToFile(save_rawdata_path, 'a', e.text + '\n')
                        company_attribute = e.text.split('\n')
                        extracted_job_info[company_attribute[0]] = company_attribute[1]
                
                clickElementAndWaitForLoading(
                    driver=driver,
                    click_find_by=By.CSS_SELECTOR,
                    click_find_value='#JobDescriptionContainer > div.css-t3xrds.e856ufb5',
                    checked_find_by=By.ID,
                    checked_find_value='JobDescriptionContainer',
                    max_wait_period=10.0,
                    wait_method='contentChange',
                    click_exception_handler='pass'
                )
                
                try:
                    job_desc = driver.find_element(by=By.ID, value='JobDescriptionContainer')
                except:
                    pass
                else:
                    logTextToFile(save_rawdata_path, 'a', job_desc.text + '\n')
                    extracted_job_info['Job Description'] = job_desc.text

                job_ls.append(extracted_job_info)
                
                logTextToFile(save_rawdata_path, 'a', '\n\n')
                
                if len(job_ls) % 10 == 0:
                    pd.DataFrame(job_ls).to_csv('tempResult.csv')
                    
                print(f'Finished in {datetime.now() - start_time} seconds.')
                
        pages = driver.find_element(by=By.CSS_SELECTOR, value='#MainCol > div.tbl.fill.px.my.d-flex > div.cell.middle.d-none.d-md-block.py-sm').text
        print(pages)
        ps = pages.split()
        print(f"Page {ps[1]} of {ps[3]}")
        
        if int(ps[1]) < int(ps[3]):
            clickElementAndWaitForLoading(driver=driver, click_find_by=By.CSS_SELECTOR,
                                      click_find_value='#FooterPageNav > div > ul > li.css-114lpwu.e1gri00l4 > a > span',
                                      checked_find_by=By.CSS_SELECTOR, 
                                      checked_find_value ="#JDCol > div > article > div > div:nth-child(1) > div > div > div.css-vwxtm.evnfo7p1 > div.css-19txzrf.e14vl8nk0 > div.css-w04er4.e1tk4kwz6",
                                      wait_method='contentChange',
                                      max_wait_period=10)
        else:
            break
        
    return pd.DataFrame(job_ls).to_csv(save_csv_path) if save_csv_path else pd.DataFrame(job_ls)
