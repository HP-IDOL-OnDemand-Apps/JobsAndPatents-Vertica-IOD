
#Requirements
1. intall pip (using pip install the below tools)
2. unixodbc-dev
2. pyodbc
3. requests
4. HP vertica client drivers to be installed on /opt/vertica
5. add odbc driver info to vim /etc/odbcinst.ini 


#Prep
Before running the script,

1. Set your IDOL OnDemand apikey in config.json 
1. create db in the box where hp vertica runs
2. use initial_setup.sql ( `/opt/vertica/bin/vsql -h <vm-ip> -d mydb -U dbadmin -f "initial_setup.sql"`), this can be done from local machine.
3. Edit config.json to give the vm-ip and the db details/ auth keys.
4. finally we can run the script by `python nyc_data_extractor.py` 
by defauls config.json and resource/nyc_company_data.csv will be used
or by giving the input and config files.


#Run

```python nyc_data_extractor.py -c config.json -i resource/nyc_company_data.csv ```


