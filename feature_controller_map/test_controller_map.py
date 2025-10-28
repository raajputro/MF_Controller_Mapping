from dotenv import load_dotenv
load_dotenv()
import os, random, sys

from faker import Faker
fake = Faker()

from rich.traceback import install
install()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from pages.page_feature_list import feature_list_page
from pages.page_feature_info import feature_info_page
from pages.page_feature_controller_mapping import feature_controller_mapping_page
from pages.page_user_access_control import user_access_control_page
from pages.page_utility import utility_page
from pages.page_voucher_mapping import voucher_mapping_page

test_env = 69  # 69 - Env69, 73 - Amar Hishab, 0 - Staging
test_user_type = 'SA'

match test_env:
    case 69:
        test_url = os.getenv('env69_url')
    case 73:
        test_url = os.getenv('amar_hishab_url')
    case _:
        test_url = os.getenv('staging_url')
        
test_branch_code = '0' if test_user_type == 'SA' else os.getenv('amar_hishab_test_branch')
test_user = os.getenv('amar_hishab_test_user_SA') if test_user_type == 'SA' else os.getenv('amar_hishab_test_user')
test_pass = os.getenv('amar_hishab_test_pass')
dfs = None

def test_00_login_to_environment(page):
    f_page = feature_list_page(page)
    f_page.perform_login(given_url=test_url, user_name=test_user, pass_word=test_pass, branch_code=test_branch_code) # type: ignore
    f_page.get_full_page_screenshot("Login SS")
    global dfs
    dfs = f_page.read_excel_file()


def test_02_map_feature_controller(page):
    f_page = feature_list_page(page)
    fi_page = feature_info_page(page)
    fcm_page = feature_controller_mapping_page(page)

    main_nav = ''
    # secn_nav = ['Menu','Feature','Feature List']
    # f_page.navigate_to_page(main_nav_val=main_nav, sub_nav_val=secn_nav)
    # f_page.get_full_page_screenshot("Feature Page SS")
    # feature_df = dfs['Features'].ffill() # type: ignore
    # # # Feature
    # # Module	Feature Info List	Feature Type	Feature Name	Feature URL
    # # # Feature Controller Mapping
    # # Module	Feature	Action	Parent Controller	Controllers    
    # data_list = feature_df.to_dict(orient='records')
    # print(data_list)
    # for dt in data_list:            # Enter each feature from excel
    #     f_page.navigate_to_page(main_nav_val=main_nav, sub_nav_val=secn_nav)
    #     f_page.perform_action(feat_name=dt['Module'], itm_name=dt['Feature Info List'])                
    #     fi_page.perform_action_2(feature_data = [dt['Feature Name'], dt['Feature URL']])
            
    # secn_nav = ['Menu','Feature','Feature Controller Mapping']
    # fcm_page.navigate_to_page(main_nav_val=main_nav, sub_nav_val=secn_nav)
    # feature_controller_map_df = dfs['Feature_Controller_Map'].ffill() # type: ignore
    # data_list = feature_controller_map_df.to_dict(orient='records')
    # print(data_list)
    # for dt in data_list:            # Enter each feature controller mapping from excel
    #     fcm_page.navigate_to_page(main_nav_val=main_nav, sub_nav_val=secn_nav)
    #     fcm_page.perform_action(data=dt)

    ###################################################################################################################################
    ###################################################################################################################################
    
    uac_page = user_access_control_page(page)
    secn_nav = ['User','Access Control','Access Control']
    # uac_page.navigate_to_page(main_nav_val=main_nav, sub_nav_val=secn_nav)
    # uac_page.get_full_page_screenshot("User Access Control SS")

    # # User Access Map
    # Role	Module	Feature_Name	Action
    uac_df = dfs['User_Access_Map'].ffill() # type: ignore
    data_list = uac_df.to_dict(orient='records')    
    print('**************************** User Access Control Data List ****************************')
    print(data_list)
    print('***************************************************************************************************************************')    
    uac_page.navigate_to_page(main_nav_val=main_nav, sub_nav_val=secn_nav)    
    print('***************************************************************************************************************************')
    print('***************************************************************************************************************************')
    for dt in data_list:            # Enter each user access control mapping from excel        
        roles = dt['Role'].split(',')
        for role in roles:
            r = role.strip().upper()            
            print('***************************************************************************************************************************')
            print(f'Setting access for Role: {r}, Module: {dt["Module"]}, Feature: {dt["Feature_Name"]}, Action: {dt["Actions"]}')
            print('***************************************************************************************************************************')
            uac_page.set_user_access_for_feature_action(role=r, module=dt['Module'], feature=dt['Feature_Name'], action=dt['Actions'])
            uac_page.wait_for_timeout(5000)

    # up_page = utility_page(page=page, base_url=test_url)
    # up_page.perform_utility_action()


# def test_03_perform_voucher_mapping(page):    
#     # # Voucher Map
#     # Project	Module	Event Type	Event	Amount Type	    Reference	Voucher Type	Dr Account Head Type	Dr Account Head	    Cr Account Head Type	Cr Account Head	    Remarks
#     main_nav = 'Accounting'
#     secn_nav = ['Admin','Feature configuration','Chart of Accounts Mapping']
#     vm_page = voucher_mapping_page(page)

#     df_voucher_map = dfs['Voucher_Map'].ffill() # type: ignore
#     data_list = df_voucher_map.to_dict(orient='records')
#     print(data_list)

#     for dt in data_list:            
#         vm_page.navigate_to_page(main_nav_val=main_nav, sub_nav_val=secn_nav)
#         coa_search_dt = {
#             'project': dt['Project'],
#             'module': dt['Module'],
#             'event_type': dt['Event Type'],
#             'event': dt['Event'],
#         }
#         coa_map_dt = [    
#             {
#                 'amount_type': dt['Amount Type'],
#                 'reference': dt['Reference'],
#                 'voucher_type': dt['Voucher Type'],
#                 'debit_head': dt['Dr Account Head'],
#                 'credit_head': dt['Cr Account Head']
#             }
#         ]
#         vm_page.perform_action(coa_search_data=coa_search_dt, coa_map_data=coa_map_dt)


def test_99_logout_from_environment(page):
    f_page = feature_list_page(page)
    f_page.perform_logout()
    f_page.get_full_page_screenshot("Logout SS")