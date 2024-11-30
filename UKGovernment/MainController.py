
from FinancialDataController import FinancialDataController
from CompanyDataController import CompanyDataController
from DbController import DbController
from FinancialHistoryController import FinancialHistoryController
from PersonDataController import PersonalDataController

import calendar
import Global
import Helper
import os
import sys

# Arguments type
## no argument: import last updated website data into our database, and then export into each company file
## -out [path]: export all data from the 3 databases into xml files for each company
###                 (if path is empty, exported into '/exp_data' folder in the same level as script)

if __name__ == "__main__":
    Global.init(__file__)

    Helper.Log('Starting UK Government data migration...', True)

    dbController = DbController()
    # Connect database
    if dbController.connectDB() == False:
        sys.exit()

    if len(sys.argv) >= 2 and sys.argv[1] == '-finhist':
        finHistoryController = FinancialHistoryController()
        for year in range(2010, 2020):
            for month in range(12):
                url = 'http://download.companieshouse.gov.uk/archive/Accounts_Monthly_Data-{0}{1}.zip'\
                                .format(calendar.month_name[month + 1], year)
                finHistoryController.migrate(url)
    elif len(sys.argv) >= 2 and sys.argv[1] == '-finhistexport':
        finHistoryController = FinancialHistoryController()
        finHistoryController.export_history()
    else:
        # Get table names in the database
        # if dbController.get_table_indices() == False:
        #     Helper.Log('Can not get table names in the database')
        #     sys.exit()

        if len(sys.argv) == 1:      # import last updated data from the website
            # Get last updated urls from the website
            db_last_updated_data = dbController.getDataLastUpdated()

            db_bcd_date = db_last_updated_data[0]
            # db_psc_date = db_last_updated_data[1]
            db_abd_date = db_last_updated_data[2]

            online_bcd_date = Helper.online_bcd_last_updated()
            # online_psc_date = Helper.online_psc_last_updated()
            online_abd_date = Helper.online_abd_last_updated()

            if online_bcd_date != None and (db_bcd_date == None or db_bcd_date < online_bcd_date):
                bcd_url = 'http://download.companieshouse.gov.uk/BasicCompanyDataAsOneFile-{0}.zip'\
                                                .format(online_bcd_date.strftime('%Y-%m-%d'))
                Helper.Log('Starting company data migration from {0}'.format(bcd_url), True)
                companyDataController = CompanyDataController()
                companyDataController.migrate(bcd_url, dbController)
                dbController.update_bcd_last_updated(online_bcd_date)
                Helper.Log('Finished company data migration', True)

            # if online_psc_date != None and (db_psc_date == None or db_psc_date < online_psc_date):
            #     psc_url = 'http://download.companieshouse.gov.uk/persons-with-significant-control-snapshot-{0}.zip'\
            #                                     .format(online_psc_date.strftime('%Y-%m-%d'))
            #     personalDataController = PersonalDataController()
            #     personalDataController.migrate(psc_url, dbController)
            #     dbController.update_psc_last_updated(online_psc_date)

            if online_abd_date != None and (db_abd_date == None or db_abd_date < online_abd_date):
                abd_url = 'http://download.companieshouse.gov.uk/Accounts_Bulk_Data-{0}.zip' \
                                                .format(online_abd_date.strftime('%Y-%m-%d'))
                Helper.Log('Starting financial data migration from {0}'.format(abd_url), True)
                financialDataController = FinancialDataController()
                financialDataController.migrate(abd_url, dbController)
                dbController.update_abd_last_updated(online_abd_date)
                Helper.Log('Finished financial data migration', True)

        elif len(sys.argv) >= 3 and sys.argv[1] == '-fin':      # import historical financial data from the website
            # dbController.export_database()
            fin_month = sys.argv[2]
            fin_url = 'http://download.companieshouse.gov.uk/Accounts_Monthly_Data-{0}.zip'.format(fin_month)
            financialDataController = FinancialDataController()
            financialDataController.migrate(fin_url, dbController)
            pass

    dbController.disconnectDB()

    Helper.Log('Finished UK Government data migration...', True)

