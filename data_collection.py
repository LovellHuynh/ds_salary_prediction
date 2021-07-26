# standard imports
from datetime import datetime

# third-party imports
import glassdoor_scraper as gs

start_time = datetime.now()
chromedriver_path = "chromedriver"
gs.get_jobs(keyword = "data scientist", num_jobs = 1000, 
                chromedriver_path = chromedriver_path, sleep_time=3,
                save_csv_path='glassdoor_jobs.csv',
                save_rawdata_path='glassdoor_jobs_raw.txt')
  
print(f'\n\n Finished in {datetime.now() - start_time} seconds.')