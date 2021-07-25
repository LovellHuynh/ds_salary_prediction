import glassdoor_scraper as gs
from datetime import datetime

if __name__ == '__main__':
  start_time = datetime.now()
  chromedriver_path = "E://MY PROJECTS//Data Science//Projects//ds_salary_prediction//chromedriver"
  gs.get_jobs(keyword = "data scientist", num_jobs = 15, 
                   chromedriver_path = chromedriver_path, sleep_time=3,
                   save_csv_path='glassdoor_jobs.csv',
                   save_rawdata_path='glassdoor_jobs_raw.txt')
  
  print(f'\n\n Finished in {datetime.now() - start_time} seconds.')