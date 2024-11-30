
import Global
import Helper
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from os import listdir
from os.path import isfile, join
from xbrl import XBRLParser, GAAP, GAAPSerializer
import random
import shutil
import string
import urllib.request
import zipfile

class FinancialHistoryController():
    def __init__(self):
        self._soup = None
        pass

    def migrate(self, url):
        zip_path = self.download_file(url)
        if not zip_path:
            return

        unzipped_path = self.unzip_file(zip_path)
        if not unzipped_path:
            return

        self.parse_directory(unzipped_path)

        # delete unzipped directory
        shutil.rmtree(unzipped_path)

    def download_file(self, url):
        try:
            # Make directory to download file
            Path(Global.data_path).mkdir(parents=True, exist_ok=True)
            local_path = os.path.join(Global.data_path, url.split('/')[-1])
            Helper.Log('%s ==> %s downloading... Please wait' % (url, Global.data_path))
            urllib.request.urlretrieve(url, local_path)
            Helper.Log('Download finished ==> %s' % local_path)
            return local_path
        except Exception as e:
            Helper.Log('Exception when downloading ==> %s' % str(e))
            return ''

    def randomString(self, stringLength=4):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def unzip_file(self, zip_path):
        try:
            # Get path to unzip downloaded file, add random string if directory is already exist
            dot_index = zip_path.rfind('.')
            unzip_dirpath = zip_path
            if dot_index > -1:
                unzip_dirpath = zip_path[:dot_index]

            while os.path.exists(unzip_dirpath):
                unzip_dirpath += self.randomString()

            Path(unzip_dirpath).mkdir(parents=True, exist_ok=True)

            # Unzip downloaded file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                Helper.Log('Unzipping %s ==> %s' % (zip_path, unzip_dirpath))
                zip_ref.extractall(unzip_dirpath)
                Helper.Log('Unzip finished ==> %s' % unzip_dirpath)
                return unzip_dirpath
        except Exception as e:
            Helper.Log('Exception when unzip ==> %s' % str(e))
            return ""

    def get_company_number_prefix(self, param):
        lower_param = param.lower()
        for c in lower_param:
            if c != '0':
                return c
        return ''

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

    def parse_directory(self, unzipped_path):
        Helper.Log('Parsing files in the unzipped path ==> %s' % unzipped_path)
        for f in listdir(unzipped_path):
            try:
                abs_path = join(unzipped_path, f)
                if isfile(abs_path):
                    run_process, company_number, balance_date = self.parse_file_name(abs_path)
                    if not company_number:
                        continue
                    company_number_prefix = self.get_company_number_prefix(company_number)
                    if not company_number_prefix:
                        continue
                    target_folder_path = os.path.join(Global.fn_history_path, 'numbers', company_number_prefix, company_number)
                    Path(target_folder_path).mkdir(parents=True, exist_ok=True)
                    target_path = os.path.join(target_folder_path, f)
                    os.rename(abs_path, target_path)
            except Exception as e:
                Helper.Log('Exception in parase_directory {0}'.format(str(e)))

    def extract_tags_in_html(self, balance_year):
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
                if 'cur' in context_ref or context_ref == 'b' or context_ref.startswith('b_') \
                        or context_ref == 'fy1.end' or str(balance_year) in context_ref:
                    financial_values['Current_{0}'.format(real_name)] = non_fraction_tag.text
                elif 'prev' in context_ref or context_ref == 'e' or context_ref.startswith('e_') \
                        or context_ref == 'fy2.end' or str(balance_year - 1) in context_ref:
                    financial_values['Previous_{0}'.format(real_name)] = non_fraction_tag.text
        return financial_values

    def extract_tags_in_xbrl(self, balance_year):
        financial_values = {}
        if (self._soup):
            tag_list = self._soup.find_all()
            financial_values = {}
            for tag in tag_list:
                if tag.name.startswith('pt:'):
                    attributes = tag.attrs
                    if 'contextref' in attributes:
                        context_ref = attributes['contextref']

                        name = tag.name
                        token_arr = name.split(':')
                        real_name = token_arr[-1]
                        if 'thisyear' in context_ref or str(balance_year) in context_ref:
                            financial_values['Current_{0}'.format(real_name)] = tag.text
                        elif 'lastyear' in context_ref or str(balance_year - 1) in context_ref:
                            financial_values['Previous_{0}'.format(real_name)] = tag.text
        return financial_values

    def export_history(self):
        folder_path = os.path.join(Global.fn_history_path, 'numbers')
        company_number = ''

        index = 0
        for company_first_letter in listdir(folder_path):
            company_group_path = os.path.join(folder_path, company_first_letter)
            for company_name in listdir(company_group_path):
                index = index + 1
                if (index % 10000) == 0:
                    Helper.Log('{0} company data handled so far'.format(str(index)), True)

                company_path = os.path.join(company_group_path, company_name)
                history_data = {}

                number_first_letter = Helper.get_company_number_prefix(company_name)
                if number_first_letter:
                    number_target_dir_path = join(Global.export_path, 'numbers', number_first_letter, 'his')
                    number_target_path = join(number_target_dir_path, '{0}-his-data.xml'.format(company_name))
                    if os.path.exists(number_target_path):
                        continue

                for f in listdir(company_path):
                    try:
                        abs_path = join(company_path, f)

                        run_process, company_number, balance_date = self.parse_file_name(abs_path)
                        if not company_number:
                            continue

                        dt = datetime.strptime(balance_date, '%Y%m%d')
                        balance_year = dt.year
                        financial_data = {}

                        if isfile(abs_path) and abs_path.endswith('.html'): # inline XBRL format
                            with open(abs_path, mode='r', encoding='utf-8') as fd:
                                file_content = fd.read()
                                self._soup = BeautifulSoup(file_content.lower(), 'html.parser')
                                financial_data = self.extract_tags_in_html(balance_year)
                        elif isfile(abs_path) and abs_path.endswith('.xml'):
                            with open(abs_path, mode='r', encoding='utf-8') as fd:
                                file_content = fd.read()
                                self._soup = BeautifulSoup(file_content.lower(), 'lxml')
                                financial_data = self.extract_tags_in_xbrl(balance_year)

                        # If can not parse file, then move to unexported folder
                        if not financial_data:
                            Path(Global.unexported_path).mkdir(parents=True, exist_ok=True)
                            bk_path = join(Global.unexported_path, f)
                            shutil.copy(abs_path, bk_path)
                        else:
                            history_data[balance_date] = financial_data
                    except Exception as e:
                        Helper.Log('Exception in export_history {0}'.format(str(e)), True)

                if not history_data:
                    Helper.export_financial_history('', company_number, history_data)
