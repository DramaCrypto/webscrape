from datetime import datetime
import Helper
from itertools import chain
import json
import mysql.connector
from mysql.connector import errorcode
from Global import CREATE_COMPANY_QUERY, INSERT_COMPANY_QUERY, UPDATE_COMPANY_QUERY, \
    CREATE_PERSON_QUERY, CREATE_FINANCIAL_QUERY, CREATE_OPTIONS_QUERY

class DbController(object):
    def __init__(self):
        self.cnx = None
        self.company_table_suffixes = []
        self.psc_table_suffixes = []
        self.financial_table_suffixes = []
        self.company_record_count_in_last_table = 0
        self.psc_last_record_no = 0
        self.financial_last_record_no = 0
        self.company_numbers = {}

    def connectDB(self):
        try:
            self.cnx = mysql.connector.connect(user='root', password='', host='127.0.0.1', database='legaldb')
            # self.cnx = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='legaldb')
            Helper.Log('Database connection success')
            return True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                Helper.Log("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                Helper.Log("Database does not exist")
            else:
                Helper.Log('Database error %s' % str(err))
            return False

    def disconnectDB(self):
        if self.cnx:
            self.cnx.close()
        pass

    def get_table_indices(self):
        try:
            cursor = self.cnx.cursor(buffered=True)
            query = 'SELECT table_name FROM information_schema.tables where table_schema="legaldb" ORDER BY table_name'
            cursor.execute(query, {})
            results = cursor.fetchall()

            # Get company and personal data table indices
            for result in results:
                table_name = result[0]
                if table_name.startswith('tbl_company'):
                    try:
                        token_arr = table_name.split('_')
                        end_token = token_arr[len(token_arr) - 1]
                        suffix = int(end_token[:len(end_token) - 1])

                        # Add company numbers in this table to the list
                        query = 'SELECT CompanyNumber FROM {0};'.format(table_name)
                        cursor.execute(query, {})
                        # company_numbers_in_this_table = set(cursor.fetchall())
                        curr_table_columns = cursor.fetchall()
                        company_numbers_in_this_table = tuple(chain(*curr_table_columns))
                        self.company_numbers[suffix] = company_numbers_in_this_table

                        # Add table suffix to the list
                        if suffix not in self.company_table_suffixes:
                            self.company_table_suffixes.append(suffix)
                    except Exception as e:
                        continue
                elif table_name.startswith('tbl_person'):
                    token_arr = table_name.split('_')
                    end_token = token_arr[len(token_arr) - 1]
                    try:
                        suffix = int(end_token[:len(end_token) - 1])
                        if suffix not in self.company_table_suffixes:
                            self.psc_table_suffixes.append(suffix)
                    except Exception as e:
                        continue

            self.company_table_suffixes.sort()
            self.psc_table_suffixes.sort()

            # Get company last record id
            if len(self.company_table_suffixes) > 0:
                last_table_index = self.company_table_suffixes[-1]
                query = 'SELECT COUNT(CompanyNumber) FROM tbl_company_{0}s'.format(last_table_index)
                cursor.execute(query, {})
                result = cursor.fetchone()
                if result:
                    self.company_record_count_in_last_table = result[0]

            # Get person last record id
            if len(self.psc_table_suffixes) > 0:
                last_table_index = self.psc_table_suffixes[-1]
                query = 'SELECT max(id) FROM tbl_person_{0}s'.format(last_table_index)
                cursor.execute(query, {})
                result = cursor.fetchone()
                if result:
                    self.psc_last_record_no = result[0]

            self.cnx.commit()
            cursor.close()

            return True
        except Exception as e:
            Helper.Log('Exception in get_table_indices function ==> %s' % str(e))
            return False

    def createCompanyTable(self):
        new_table_index = 5
        if len(self.company_table_suffixes) > 0:
            new_table_index = self.company_table_suffixes[-1] + 5
        cursor = self.cnx.cursor(buffered=True)
        create_table_query = CREATE_COMPANY_QUERY.format(new_table_index)
        cursor.execute(create_table_query, {})

        self.cnx.commit()
        cursor.close()
        self.company_table_suffixes.append(new_table_index)
        self.company_numbers[new_table_index] = tuple()
        self.company_record_count_in_last_table = 0
        Helper.Log('New table was created {0}'.format(new_table_index))

    def insertCompanyData(self, record_data):
        try:
            Helper.export_company(record_data)
        except Exception as e:
            Helper.Log('Exception in insertCompanyData function ==> %s' % str(e))
            pass

    def insertCompanyData__(self, record_data):
        try:
            cursor = self.cnx.cursor(buffered=True)
            company_number = record_data[1]
            query = ''
            already_exist = False

            # Check if company exists in the current database
            for key in self.company_numbers.keys():
                company_numbers_pieces = self.company_numbers[key]
                if company_number in company_numbers_pieces:
                    query = UPDATE_COMPANY_QUERY.format(key, company_number)
                    cursor.execute(query, record_data)
                    already_exist = True
                    break

            if not already_exist:                # If not exist, insert new data
                if self.company_record_count_in_last_table >= 500000 or len(self.company_table_suffixes) == 0:
                    self.createCompanyTable()

                # add company to the last index of table
                last_table_index = self.company_table_suffixes[-1]
                add_company_query = INSERT_COMPANY_QUERY.format(last_table_index, record_data)
                cursor.execute(add_company_query, {})

                # Add this company number to the set so that can be used to check later
                company_numbers_pieces = self.company_numbers[last_table_index]
                self.company_numbers[last_table_index] = company_numbers_pieces + (company_number,)

                # Add the record count in the last company table
                self.company_record_count_in_last_table = self.company_record_count_in_last_table + 1

            Helper.export_company(record_data)

            self.cnx.commit()
            cursor.close()
        except Exception as e:
            Helper.Log('Exception in insertCompanyData function ==> %s' % str(e))
            pass

    def createPersonTable(self):
        new_table_index = 5
        if len(self.psc_table_suffixes) > 0:
            new_table_index = self.psc_table_suffixes[-1] + 5
        cursor = self.cnx.cursor(buffered=True)
        create_table_query = CREATE_PERSON_QUERY.format(new_table_index)
        cursor.execute(create_table_query, {})

        self.cnx.commit()
        cursor.close()
        self.psc_table_suffixes.append(new_table_index)
        self.psc_last_record_no = 0

    def insertPersonData(self, record_data):
        try:
            cursor = self.cnx.cursor(buffered=True)
            links_self = record_data[14]
            query = ''
            index = 0
            already_exist = False

            # Check if person exists in the current database
            if len(self.psc_table_suffixes) > 0:
                for suffix in self.psc_table_suffixes:
                    query += 'SELECT links_self FROM tbl_person_{0}s WHERE links_self="{1}";' \
                                                .format(suffix, links_self)

                for result in cursor.execute(query, {}, multi=True):
                    if result.rowcount > 0:  # If exist, then update person data
                        suffix = self.psc_table_suffixes[index]
                        query = (
                            "UPDATE tbl_person_{0}s SET company_number=%s,address_line_1=%s,address_line_2=%s,country=%s,"
                            "locality=%s,postal_code=%s,premises=%s,region=%s,ceased_on=%s,country_of_residence=%s,"
                            "date_of_birth_month=%s,date_of_birth_year=%s,etag=%s,kind=%s,links_self=%s,name=%s,"
                            "forename=%s,middle_name=%s,surname=%s,name_title=%s,nationality=%s,natures_of_control=%s,notified_on=%s"
                            "WHERE links_self={1}").format(suffix, links_self)
                        cursor.execute(query, record_data)
                        already_exist = True
                        break
                    index = index + 1

            if not already_exist:                # If not exist, insert new data
                if self.psc_last_record_no >= 500000 or len(self.psc_table_suffixes) == 0:
                    self.createPersonTable()

                # add company to the last index of table
                last_table_index = self.psc_table_suffixes[-1]
                add_person_query = ("INSERT INTO tbl_person_{0}s (company_number,address_line_1,address_line_2,country,"
                                    "locality,postal_code,premises,region,ceased_on,country_of_residence,date_of_birth_month,"
                                "date_of_birth_year,etag,kind,links_self,name,forename,middle_name,surname,name_title,"
                                "nationality,natures_of_control,notified_on) "
                                  "VALUES {1}").format(last_table_index, record_data)
                cursor.execute(add_person_query, {})
                self.psc_last_record_no = self.psc_last_record_no + 1
            self.cnx.commit()
            cursor.close()
        except Exception as e:
            Helper.Log('Exception in insertPersonData function ==> %s' % str(e))

    # Create account table if not exist
    def createFinancialTable(self, table_name):
        try:
            cursor = self.cnx.cursor(buffered=True)
            check_table_query = 'SELECT 1 FROM `{0}` LIMIT 1'.format(table_name)
            should_create_table = False
            try:
                cursor.execute(check_table_query, {})
            except Exception as e:
                error_msg_pattern = '{0}\' doesn\'t exist'.format(table_name)
                if str(e).endswith(error_msg_pattern):
                    should_create_table = True

            if should_create_table:
                create_table_query = CREATE_FINANCIAL_QUERY.format(table_name)
                cursor.execute(create_table_query, {})
                self.cnx.commit()
            cursor.close()
        except Exception as e:
            Helper.Log('Exception in createAccountTable function ==> %s' % str(e))

    # Insert account data into table
    def insertFinancialData__(self, table_name, zip_name, run_process, company_number, balance_date, financial_data):
        try:
            self.createFinancialTable(table_name)
            cursor = self.cnx.cursor(buffered=True)
            add_account_query = (
                "INSERT INTO {0} (zip_name, run_process, company_number, balance_date, financial_values) "
                "VALUES ('{1}','{2}','{3}','{4}','{5}')".
                format(table_name, zip_name, run_process, company_number, balance_date, json.dumps(financial_data)))
            cursor.execute(add_account_query, {})

            company_name = ''
            for key in self.company_numbers.keys():
                company_numbers_pieces = self.company_numbers[key]
                if company_number in company_numbers_pieces:
                    query = 'SELECT CompanyName FROM tbl_company_{0}s WHERE CompanyNumber={1}' \
                        .format(key, company_number)
                    cursor.execute(query, {})
                    result = cursor.fetchone()
                    if result:
                        company_name = result[0]

            self.cnx.commit()
            cursor.close()

            Helper.export_financial(company_name, company_number, balance_date, financial_data)
        except Exception as e:
            Helper.Log('Exception in insertAccountData function ==> %s' % str(e))

    # Insert account data into table
    def insertFinancialData(self, table_name, zip_name, run_process, company_number, balance_date, financial_data):
        try:
            company_name = ''
            Helper.export_financial(company_name, company_number, balance_date, financial_data)
        except Exception as e:
            Helper.Log('Exception in insertAccountData function ==> %s' % str(e))

    #################################################################################################################
    # Create tbl_options table if not exist
    def createOptionsTable(self):
        try:
            cursor = self.cnx.cursor(buffered=True)
            check_table_query = 'SELECT 1 FROM `tbl_options` LIMIT 1'
            should_create_table = False
            try:
                cursor.execute(check_table_query, {})
            except Exception as e:
                error_msg_pattern = 'tbl_options\' doesn\'t exist'
                if str(e).endswith(error_msg_pattern):
                    should_create_table = True

            if should_create_table:
                cursor.execute(CREATE_OPTIONS_QUERY, {})

            # check if there is one record exist in the options table
            query = 'SELECT count(*) FROM tbl_options'
            cursor.execute(query, {})
            result = cursor.fetchone()
            if not result or result[0] == 0:
                query = 'INSERT INTO `tbl_options`(`id`) VALUES(NULL)'
                cursor.execute(query, {})

            self.cnx.commit()
            cursor.close()
        except Exception as e:
            Helper.Log('Exception in createOptionsTable function ==> %s' % str(e))

    # Get last updated date for the company, personal and financial data
    def getDataLastUpdated(self):
        try:
            self.createOptionsTable()
            cursor = self.cnx.cursor(buffered=True)
            query = 'SELECT bcd_last_updated, psc_last_updated, abd_last_updated from tbl_options'
            cursor.execute(query, {})
            result = cursor.fetchone()
            self.cnx.commit()
            cursor.close()
            return result
        except Exception as e:
            Helper.Log('Exception in getDataLastUpdated function ==> %s' % str(e))

    # Update company last updated date
    def update_bcd_last_updated(self, last_updated):
        try:
            cursor = self.cnx.cursor(buffered=True)
            query = 'UPDATE tbl_options SET bcd_last_updated="{0}"'.format(last_updated)
            cursor.execute(query, {})
            self.cnx.commit()
            cursor.close()
            return True
        except Exception as e:
            Helper.Log('Exception in update_bcd_last_updated function ==> %s' % str(e))
            return False

    # Update personal last updated date
    def update_psc_last_updated(self, last_updated):
        try:
            cursor = self.cnx.cursor(buffered=True)
            query = 'UPDATE tbl_options SET psc_last_updated="{0}"'.format(last_updated)
            cursor.execute(query, {})
            self.cnx.commit()
            cursor.close()
            return True
        except Exception as e:
            Helper.Log('Exception in update_bcd_last_updated function ==> %s' % str(e))
            return False

    # Update finanical data last updated date
    def update_abd_last_updated(self, last_updated):
        try:
            cursor = self.cnx.cursor(buffered=True)
            query = 'UPDATE tbl_options SET abd_last_updated="{0}"'.format(last_updated)
            cursor.execute(query, {})
            self.cnx.commit()
            cursor.close()
            return True
        except Exception as e:
            Helper.Log('Exception in update_bcd_last_updated function ==> %s' % str(e))
            return False
    #################################################################################################################