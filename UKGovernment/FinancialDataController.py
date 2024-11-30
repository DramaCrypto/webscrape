from BaseController import BaseController
from bs4 import BeautifulSoup
import Helper
import os
from xbrl import XBRLParser, GAAP, GAAPSerializer

class FinancialDataController(BaseController):
    def __init__(self):
        self.table_name = 'tbl_account_'
        self.zip_name = ''
        self._soup = None
        pass

    def migrate(self, url, db_controller):
        # self.local_path = 'F:\\task\\webscrapping\\UKGovernment\\data\\Accounts_Bulk_Data-2020-04-25.zip'
        # self.unzipped_path = 'F:\\task\\webscrapping\\UKGovernment\\data\\Accounts_Bulk_Data-2020-04-25'
        self.parse_zip_name(url)
        BaseController.migrate(self, url, db_controller)
        pass

    # get database table name from the link
    def parse_zip_name(self, zip_link):
        try:
            self.zip_name = os.path.basename(zip_link)
            start_index = zip_link.rfind('Accounts_Bulk_Data-')
            last_index = zip_link.rfind('.zip')

            if start_index == -1 or last_index == -1 or start_index + 19 > last_index:
                self.table_name = 'tbl_account_nondate'
            else:
                date_string = zip_link[(start_index + 19):last_index]
                date_string = ''.join(date_string.split('-'))[:6]
                self.table_name = 'tbl_account_{0}'.format(date_string)
        except Exception as e:
            Helper.Log('Exception in parse_zip_name function {0}'.format(str(e)))

    def parse_file_name(self, file_path):
        try:
            file_name = os.path.basename(file_path)
            first_index = file_name.find('_')
            second_index = file_name.find('_', first_index + 1)
            third_index = file_name.find('_', second_index + 1)
            dot_index = file_name.rfind('.')
            if first_index == -1 or second_index == -1 or third_index == -1 or dot_index == -1:
                return '', '', ''
            run_process = file_name[:second_index]
            company_number = file_name[second_index + 1:third_index]
            balance_date = file_name[third_index + 1:dot_index]
            return run_process, company_number, balance_date
        except Exception as e:
            Helper.Log('Exception in parse_file_name function {0}'.format(str(e)))

    def extract_tags(self):
        financial_values = {}
        if (self._soup):
            non_fraction_tags = self._soup.findAll('ix:nonfraction')
            for non_fraction_tag in non_fraction_tags:
                if not non_fraction_tag.has_attr('contextref'):
                    continue
                if not non_fraction_tag.has_attr('name'):
                    continue
                context_ref = non_fraction_tag['contextref']
                name = non_fraction_tag['name']
                token_arr = name.split(':')
                real_name = token_arr[-1]
                if 'cur' in context_ref or context_ref == 'b' or context_ref.startswith('b_') or context_ref == 'fy1.end':
                    financial_values['Current_{0}'.format(real_name)] = non_fraction_tag.text
                elif 'prev' in context_ref or context_ref == 'e' or context_ref.startswith('e_') or context_ref == 'fy2.end':
                    financial_values['Previous_{0}'.format(real_name)] = non_fraction_tag.text
        return financial_values

    def parse_file(self, file_name):
        try:
            BaseController.parse_file(self, file_name)

            if file_name.endswith('.html'):     # inline XBRL format
                with open(file_name, mode='r', encoding='utf-8') as fd:
                    file_content = fd.read()
                    self._soup = BeautifulSoup(file_content.lower(), 'html.parser')

                    # First get current assets value
                    run_process, company_number, balance_date = self.parse_file_name(file_name)
                    financial_data = self.extract_tags()
                    if len(financial_data) == 0:
                        pass
                    self.db_controller.insertFinancialData(self.table_name, self.zip_name,
                                                           run_process, company_number, balance_date, financial_data)
            elif file_name.endswith('.xml'):    # XBRL format
                # xbrl_parser = XBRLParser()
                # xbrl = xbrl_parser.parse(file_name)
                pass
        except Exception as e:
            Helper.Log('Exception in parse_file function ==> {0}'.format(str(e)))

