import Helper
import os

CREATE_COMPANY_QUERY = 'CREATE TABLE `tbl_company_{0}s` ( ' \
 '`CompanyName` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`CompanyNumber` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, ' \
 '`CompanyCategory` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`CompanyStatus` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`CountryOfOrigin` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`LimitedPartnerships_NumGenPartners` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`LimitedPartnerships_NumLimPartners` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`URI` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`Accounts_AccountRefDay` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`Accounts_AccountRefMonth` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`Accounts_NextDueDate` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, '\
 '`Accounts_LastMadeUpDate` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`Accounts_AccountCategory` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`DissolutionDate` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`IncorporationDate` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`Returns_NextDueDate` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`Returns_LastMadeUpDate` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`ConfStmtNextDueDate` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`ConfStmtLastMadeUpDate` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`Mortgages_NumMortCharges` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`Mortgages_NumMortOutstanding` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`Mortgages_NumMortPartSatisfied` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`Mortgages_NumMortSatisfied` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_1_CONDATE` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_1_CompanyName` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_2_CONDATE` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_2_CompanyName` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_3_CONDATE` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_3_CompanyName` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_4_CONDATE` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_4_CompanyName` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_5_CONDATE` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_5_CompanyName` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_6_CONDATE` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_6_CompanyName` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_7_CONDATE` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_7_CompanyName` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_8_CONDATE` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_8_CompanyName` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_9_CONDATE` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_9_CompanyName` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_10_CONDATE` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`PreviousName_10_CompanyName` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`RegAddress_CareOf` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`RegAddress_POBox` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`RegAddress_AddressLine1` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`RegAddress_AddressLine2` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`RegAddress_PostTown` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`RegAddress_County` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`RegAddress_Country` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`RegAddress_PostCode` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`SICCode_SicText_1` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`SICCode_SicText_2` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`SICCode_SicText_3` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`SICCode_SicText_4` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`createdAt` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),' \
 '`updatedAt` datetime(0) NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0),' \
 'PRIMARY KEY (`CompanyNumber`) USING BTREE' \
 ') ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;'

INSERT_COMPANY_QUERY = ("INSERT INTO tbl_company_{0}s (CompanyName, CompanyNumber,RegAddress_CareOf,RegAddress_POBox,"
 "RegAddress_AddressLine1, RegAddress_AddressLine2,RegAddress_PostTown,RegAddress_County,"
 "RegAddress_Country,RegAddress_PostCode,CompanyCategory,CompanyStatus,CountryOfOrigin,"
 "DissolutionDate,IncorporationDate,Accounts_AccountRefDay,Accounts_AccountRefMonth,"
 "Accounts_NextDueDate,Accounts_LastMadeUpDate,Accounts_AccountCategory,Returns_NextDueDate,"
 "Returns_LastMadeUpDate,Mortgages_NumMortCharges,Mortgages_NumMortOutstanding,"
 "Mortgages_NumMortPartSatisfied,Mortgages_NumMortSatisfied,SICCode_SicText_1,SICCode_SicText_2,"
 "SICCode_SicText_3,SICCode_SicText_4,LimitedPartnerships_NumGenPartners,LimitedPartnerships_NumLimPartners,"
 "URI,PreviousName_1_CONDATE,PreviousName_1_CompanyName,PreviousName_2_CONDATE,PreviousName_2_CompanyName,"
 "PreviousName_3_CONDATE,PreviousName_3_CompanyName,PreviousName_4_CONDATE, PreviousName_4_CompanyName,"
 "PreviousName_5_CONDATE,PreviousName_5_CompanyName,PreviousName_6_CONDATE,PreviousName_6_CompanyName,"
 "PreviousName_7_CONDATE,PreviousName_7_CompanyName,PreviousName_8_CONDATE,PreviousName_8_CompanyName,"
 "PreviousName_9_CONDATE,PreviousName_9_CompanyName,PreviousName_10_CONDATE,PreviousName_10_CompanyName,"
 "ConfStmtNextDueDate,ConfStmtLastMadeUpDate) VALUES {1}")

UPDATE_COMPANY_QUERY = ("UPDATE tbl_company_{0}s SET CompanyName=%s,CompanyNumber=%s,RegAddress_CareOf=%s,"
 "RegAddress_POBox=%s,RegAddress_AddressLine1=%s, RegAddress_AddressLine2=%s,RegAddress_PostTown=%s,RegAddress_County=%s,"
 "RegAddress_Country=%s,RegAddress_PostCode=%s,CompanyCategory=%s,CompanyStatus=%s,CountryOfOrigin=%s,"
 "DissolutionDate=%s,IncorporationDate=%s,Accounts_AccountRefDay=%s,Accounts_AccountRefMonth=%s,"
 "Accounts_NextDueDate=%s,Accounts_LastMadeUpDate=%s,Accounts_AccountCategory=%s,Returns_NextDueDate=%s,"
 "Returns_LastMadeUpDate=%s,Mortgages_NumMortCharges=%s,Mortgages_NumMortOutstanding=%s,"
 "Mortgages_NumMortPartSatisfied=%s,Mortgages_NumMortSatisfied=%s,SICCode_SicText_1=%s,SICCode_SicText_2=%s,"
 "SICCode_SicText_3=%s,SICCode_SicText_4=%s,LimitedPartnerships_NumGenPartners=%s,LimitedPartnerships_NumLimPartners=%s,"
 "URI=%s,PreviousName_1_CONDATE=%s,PreviousName_1_CompanyName=%s,PreviousName_2_CONDATE=%s,PreviousName_2_CompanyName=%s,"
 "PreviousName_3_CONDATE=%s, PreviousName_3_CompanyName=%s,PreviousName_4_CONDATE=%s, PreviousName_4_CompanyName=%s,PreviousName_5_CONDATE=%s,"
 "PreviousName_5_CompanyName=%s,PreviousName_6_CONDATE=%s,PreviousName_6_CompanyName=%s,PreviousName_7_CONDATE=%s,"
 "PreviousName_7_CompanyName=%s,PreviousName_8_CONDATE=%s,PreviousName_8_CompanyName=%s,PreviousName_9_CONDATE=%s,"
 "PreviousName_9_CompanyName=%s,PreviousName_10_CONDATE=%s,PreviousName_10_CompanyName=%s,ConfStmtNextDueDate=%s,ConfStmtLastMadeUpDate=%s "
 "WHERE CompanyNumber=\"{1}\"")

CREATE_PERSON_QUERY = 'CREATE TABLE `tbl_person_{0}s` ( ' \
 '`links_self` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, ' \
 '`company_number` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, ' \
 '`address_line_1` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`address_line_2` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`country` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`locality` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`postal_code` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`region` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`country_of_residence` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`ceased_on` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`date_of_birth_month` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`date_of_birth_year` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`notified_on` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`forename` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`middle_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`surname` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`name_title` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`premises` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`etag` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`kind` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`nationality` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`natures_of_control` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, ' \
 '`createdAt` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),' \
 '`updatedAt` datetime(0) NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0),' \
 'PRIMARY KEY (`links_self`,`company_number`) USING BTREE' \
 ') ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;'

CREATE_FINANCIAL_QUERY = 'CREATE TABLE `{0}` (' \
 '`id` int(11) NOT NULL AUTO_INCREMENT, ' \
 '`zip_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci  NOT NULL, ' \
 '`run_process` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL, ' \
 '`company_number` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL, ' \
 '`balance_date` varchar(8) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL, ' \
 '`financial_values` text CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL, ' \
 'PRIMARY KEY (`id`)) ' \
 'ENGINE=InnoDB DEFAULT CHARSET=utf8'

CREATE_OPTIONS_QUERY = 'CREATE TABLE `tbl_options` ( ' \
 '`id` int(0) NOT NULL AUTO_INCREMENT, ' \
 '`bcd_last_updated` datetime(0) NULL DEFAULT NULL COMMENT "Basic company data last updated date", ' \
 '`psc_last_updated` datetime(0) NULL DEFAULT NULL COMMENT "Person with significant control last updated date ", ' \
 '`abd_last_updated` datetime(0) NULL DEFAULT NULL COMMENT "Accounts bulk data last updated date", ' \
 '`createdAt` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),' \
 '`updatedAt` datetime(0) NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0),' \
 'PRIMARY KEY (`id`) USING BTREE' \
 ') ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;'

top_level_path = ''
data_path = ''
export_path = ''
unexported_path = ''
fn_history_path = ''
report_path = ''

def init(main_script):
    global CREATE_COMPANY_QUERY
    global INSERT_COMPANY_QUERY
    global UPDATE_COMPANY_QUERY

    global CREATE_PERSON_QUERY
    global CREATE_FINANCIAL_QUERY
    global CREATE_OPTIONS_QUERY

    global top_level_path
    global data_path
    global export_path
    global unexported_path
    global fn_history_path
    global report_path

    top_level_path = os.path.dirname(os.path.realpath(main_script))
    data_path = os.path.join(top_level_path, 'data')
    # data_path = '/media/dbdev/sdb/data/tmp/'
    export_path = os.path.join(top_level_path, 'export')
    # export_path = '/media/winshare/uk_data/'
    unexported_path = os.path.join(top_level_path, 'unexported')
    # export_path = '/media/dbdev/sdb/data/unexported/'
    report_path = os.path.join(top_level_path, 'report')
    # report_path = '/media/winshare/uk_data/report/'
    fn_history_path = os.path.join(top_level_path, 'fn_history_test')
    # fn_history_path = '/media/dbdev/sdb/fn_history/'
