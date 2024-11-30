from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import Global
import os
import urllib.request
import xml.etree.cElementTree as ET

def Log(msg, tofile = False):
    now = datetime.now()
    print('{0} ===> {1}'.format(now.strftime('%Y-%m-%d %H:%M:%S'), msg))
    if tofile:
        Path(Global.report_path).mkdir(parents=True, exist_ok=True)
        export_file_name = 'report_{0}.txt'.format(now.strftime('%Y-%m-%d'))
        export_file_path = os.path.join(Global.report_path, export_file_name)
        with open(export_file_path, "a") as text_file:
            print('{0} ===> {1}'.format(now.strftime('%Y-%m-%d %H:%M:%S'), msg), file=text_file)

# Basic company data
def online_bcd_last_updated():
    last_updated = None
    try:
        page = urllib.request.urlopen('http://download.companieshouse.gov.uk/en_output.html');
        page_content = page.read()
        bsoup = BeautifulSoup(page_content.lower(), 'html.parser')
        last_updated_mark_tag = bsoup.find("strong", text="last updated:")
        if (last_updated_mark_tag):
            last_updated_date_str = last_updated_mark_tag.next_sibling.strip()
            last_updated = datetime.strptime(last_updated_date_str, '%d/%m/%Y')
    except Exception as e:
        print(str(e))

    return last_updated

# People with significant control (PSC)
def online_psc_last_updated():
    last_updated = None
    try:
        page = urllib.request.urlopen('http://download.companieshouse.gov.uk/en_pscdata.html');
        page_content = page.read()
        bsoup = BeautifulSoup(page_content.lower(), 'html.parser')
        last_updated_mark_tag = bsoup.find("strong", text="last updated:")
        if (last_updated_mark_tag):
            last_updated_date_str = last_updated_mark_tag.next_sibling.strip()
            last_updated = datetime.strptime(last_updated_date_str, '%d/%m/%Y')
    except Exception as e:
        print(e)

    return last_updated

# Accounts bulk data
def online_abd_last_updated():
    last_updated = None
    try:
        page = urllib.request.urlopen('http://download.companieshouse.gov.uk/en_accountsdata.html');
        page_content = page.read()
        bsoup = BeautifulSoup(page_content.lower(), 'html.parser')
        last_updated_mark_tag = bsoup.find("strong", text="last updated:")
        if (last_updated_mark_tag):
            last_updated_date_str = last_updated_mark_tag.next_sibling.strip()
            last_updated = datetime.strptime(last_updated_date_str, '%d/%m/%Y')

    except Exception as e:
        print(e)

    return last_updated

def get_company_number_prefix(param):
    lower_param = param.lower()
    if lower_param.startswith('ic'):
        return 'ic'
    elif lower_param.startswith('ip'):
        return 'ip'
    elif lower_param.startswith('np'):
        return 'np'
    elif lower_param.startswith('nr'):
        return 'nr'
    elif lower_param.startswith('nv'):
        return 'nv'
    if lower_param.startswith('rc'):
        return 'rc'
    if lower_param.startswith('rs'):
        return 'rs'
    if lower_param.startswith('sc'):
        return 'sc'
    if lower_param.startswith('si'):
        return 'si'
    if lower_param.startswith('sp'):
        return 'sp'
    if lower_param.startswith('sr'):
        return 'sr'
    for c in param:
        if c != '0':
            if c.isnumeric():
                return c
            else:
                break
    return ''

def format_company_name(param):
    formatted_name = ''
    for c in param:
        if c == '!' or c == '@' or c == '#' or c == '$' or c == '%' or c == ' ' \
                or c == '^' or c == '&' or c == '(' or c == ')' or c == ',' or c.isalnum():
            formatted_name = formatted_name + c

    return formatted_name.lstrip()

# Export company data to file
def export_company(company_data):
    if len(company_data) < 55:
        return False
    company_name = company_data[0]
    company_number = company_data[1]
    root_node = ET.Element('Result')
    root_node.set('xmlns', 'http://www.companieshouse.gov.uk/terms/xxx')

    primary_topic_node = ET.SubElement(root_node, 'primaryTopic')
    href = 'http://business.data.gov.uk/id/company/{0}'.format(company_number)
    primary_topic_node.set('href', href)

    company_name_node = ET.SubElement(primary_topic_node, 'CompanyName')
    company_name_node.text = company_name
    company_number_node = ET.SubElement(primary_topic_node, 'CompanyNumber')
    company_number_node.text = company_number

    regaddress_node = ET.SubElement(primary_topic_node, 'RegAddress')
    href = 'http://business.data.gov.uk/id/company/{0}#RegAddress'.format(company_number)
    regaddress_node.set('href', href)
    careof_node = ET.SubElement(regaddress_node, 'CareOf')
    careof_node.text = company_data[2]
    pobox_node = ET.SubElement(regaddress_node, 'POBox')
    pobox_node.text = company_data[3]
    addressline1_node = ET.SubElement(regaddress_node, 'AddressLine1')
    addressline1_node.text = company_data[4]
    addressline2_node = ET.SubElement(regaddress_node, 'AddressLine2')
    addressline2_node.text = company_data[5]
    post_town_node = ET.SubElement(regaddress_node, 'PostTown')
    post_town_node.text = company_data[6]
    county_node = ET.SubElement(regaddress_node, 'County')
    county_node.text = company_data[7]
    country_node = ET.SubElement(regaddress_node, 'Country')
    country_node.text = company_data[8]
    post_code_node = ET.SubElement(regaddress_node, 'Postcode')
    post_code_node.text = company_data[9]

    company_category_node = ET.SubElement(primary_topic_node, 'CompanyCategory')
    company_category_node.text = company_data[10]
    company_status_node = ET.SubElement(primary_topic_node, 'CompanyStatus')
    company_status_node.text = company_data[11]
    country_of_origin_node = ET.SubElement(primary_topic_node, 'CountryOfOrigin')
    country_of_origin_node.text = company_data[12]
    dissolution_date_node = ET.SubElement(primary_topic_node, 'DissolutionDate')
    dissolution_date_node.text = company_data[13]
    incorporation_date_node = ET.SubElement(primary_topic_node, 'IncorporationDate')
    incorporation_date_node.text = company_data[14]

    accounts_node = ET.SubElement(primary_topic_node, 'Accounts')
    href = 'http://business.data.gov.uk/id/company/{0}#Accounts'.format(company_number)
    accounts_node.set('href', href)
    account_ref_day_node = ET.SubElement(accounts_node, 'AccountRefDay')
    account_ref_day_node.text = company_data[15]
    account_ref_month_node = ET.SubElement(accounts_node, 'AccountRefMonth')
    account_ref_month_node.text = company_data[16]
    next_due_date_node = ET.SubElement(accounts_node, 'NextDueDate')
    next_due_date_node.text = company_data[17]
    lastmade_update_node = ET.SubElement(accounts_node, 'LastMadeUpDate')
    lastmade_update_node.text = company_data[18]
    account_category_node = ET.SubElement(accounts_node, 'AccountCategory')
    account_category_node.text = company_data[19]

    returns_node = ET.SubElement(primary_topic_node, 'Returns')
    href = 'http://business.data.gov.uk/id/company/{0}#Returns'.format(company_number)
    returns_node.set('href', href)
    returns_next_due_date_node = ET.SubElement(returns_node, 'NextDueDate')
    returns_next_due_date_node.text = company_data[20]
    returns_lastmade_update_node = ET.SubElement(returns_node, 'LastMadeUpDate')
    returns_lastmade_update_node.text = company_data[21]

    sic_codes_node = ET.SubElement(primary_topic_node, 'SICCodes')
    href = 'http://business.data.gov.uk/id/company/{0}#SICCodes'.format(company_number)
    sic_codes_node.set('href', href)
    sic_text_1_node = ET.SubElement(sic_codes_node, 'SicText_1')
    sic_text_1_node.text = company_data[26]
    sic_text_2_node = ET.SubElement(sic_codes_node, 'SicText_2')
    sic_text_2_node.text = company_data[27]
    sic_text_3_node = ET.SubElement(sic_codes_node, 'SicText_3')
    sic_text_3_node.text = company_data[28]
    sic_text_4_node = ET.SubElement(sic_codes_node, 'SicText_4')
    sic_text_4_node.text = company_data[29]

    tree = ET.ElementTree(root_node)

    number_first_letter = get_company_number_prefix(company_number)
    if number_first_letter:
        number_target_dir_path = os.path.join(Global.export_path, 'numbers', number_first_letter, 'co')
        Path(number_target_dir_path).mkdir(parents=True, exist_ok=True)
        number_target_path = os.path.join(number_target_dir_path, '{0}-co-data.xml'.format(company_number))
        tree.write(number_target_path)
    else:
        Log('[export_company] Company number invalid ==> {0}, data is {1}'.format(company_number, str(company_data)), True)

    formatted_company_name = format_company_name(company_name)
    if formatted_company_name:
        name_first_letter = formatted_company_name[0]
        name_target_dir_path = os.path.join(Global.export_path, 'names', name_first_letter, 'co')
        Path(name_target_dir_path).mkdir(parents=True, exist_ok=True)
        name_target_path = os.path.join(name_target_dir_path, '{0}-co-data.xml'.format(formatted_company_name))
        tree.write(name_target_path)
    else:
        Log('[export_company] Company name invalid ==> {0}, data is {1}'.format(company_name, str(company_data)), True)

# Export financial data to file
def export_financial(company_name, company_number, balance_date, financial_data):

    root_node = ET.Element('Result')
    root_node.set('xmlns', 'http://www.companieshouse.gov.uk/terms/xxx')

    company_number_node = ET.SubElement(root_node, 'CompanyNumber')
    company_number_node.text = company_number

    financial_node = ET.SubElement(root_node, 'financial')
    financial_node.set('balance_date', balance_date)

    for key in financial_data.keys():
        financial_value = financial_data[key]
        new_node = ET.SubElement(financial_node, key)
        new_node.text = financial_value

    if len(financial_data) == 0:
        Log('Extracting financial data failed ==> {0} {1} '.format(company_number, balance_date), True)

    tree = ET.ElementTree(root_node)

    number_first_letter = get_company_number_prefix(company_number)
    if number_first_letter:
        number_target_dir_path = os.path.join(Global.export_path, 'numbers', number_first_letter, 'fin')
        Path(number_target_dir_path).mkdir(parents=True, exist_ok=True)
        number_target_path = os.path.join(number_target_dir_path, '{0}-fin-data.xml'.format(company_number))
        tree.write(number_target_path)
    else:
        Log('[export_financial] Company number invalid ==> {0}, data is {1}'.format(company_number, str(financial_data)), True)

    formatted_company_name = format_company_name(company_name)
    if formatted_company_name:
        name_first_letter = formatted_company_name[0]
        name_target_dir_path = os.path.join(Global.export_path, 'names', name_first_letter, 'co')
        Path(name_target_dir_path).mkdir(parents=True, exist_ok=True)
        name_target_path = os.path.join(name_target_dir_path, '{0}-co-data.xml'.format(formatted_company_name))
        tree.write(name_target_path)
    else:
        Log('[export financial] Company name invalid ==> {0}, data is {1}'.format(company_name, str(financial_data)), True)

# Export financial data to file
def export_financial_history(company_name, company_number, history_data):

    root_node = ET.Element('Result')
    root_node.set('xmlns', 'http://www.companieshouse.gov.uk/terms/xxx')

    company_number_node = ET.SubElement(root_node, 'CompanyNumber')
    company_number_node.text = company_number

    for balance_date in history_data.keys():
        financial_node = ET.SubElement(root_node, 'financial')
        financial_node.set('balance_date', balance_date)

        financial_data = history_data[balance_date]
        for key in financial_data.keys():
            financial_value = financial_data[key]
            new_node = ET.SubElement(financial_node, key)
            new_node.text = financial_value

    tree = ET.ElementTree(root_node)

    number_first_letter = get_company_number_prefix(company_number)
    if number_first_letter:
        number_target_dir_path = os.path.join(Global.export_path, 'numbers', number_first_letter, 'his')
        Path(number_target_dir_path).mkdir(parents=True, exist_ok=True)
        number_target_path = os.path.join(number_target_dir_path, '{0}-his-data.xml'.format(company_number))
        tree.write(number_target_path)
    else:
        Log('[export_financial] Company number invalid ==> {0}, data is {1}'.format(company_number, str(history_data)), True)

    # formatted_company_name = format_company_name(company_name)
    # if formatted_company_name:
    #     name_first_letter = formatted_company_name[0]
    #     name_target_dir_path = os.path.join(Global.export_path, 'names', name_first_letter, 'co')
    #     Path(name_target_dir_path).mkdir(parents=True, exist_ok=True)
    #     name_target_path = os.path.join(name_target_dir_path, '{0}-co-data.xml'.format(formatted_company_name))
    #     tree.write(name_target_path)
    # else:
    #     Log('[export financial] Company name invalid ==> {0}, data is {1}'.format(company_name, str(financial_data)), True)
