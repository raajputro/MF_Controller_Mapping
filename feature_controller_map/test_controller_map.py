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


def test_00_login_to_environment(page):
    f_page = feature_list_page(page)
    f_page.perform_login(given_url=test_url, user_name=test_user, pass_word=test_pass, branch_code=test_branch_code) # type: ignore
    f_page.get_full_page_screenshot("Login SS")


def test_02_map_feature_controller(page):
    f_page = feature_list_page(page)
    fi_page = feature_info_page(page)
    fcm_page = feature_controller_mapping_page(page)
    
    dfs = f_page.read_excel_file()
    main_nav = ''
    secn_nav = ['Menu','Feature','Feature List']
    f_page.navigate_to_page(main_nav_val=main_nav, sub_nav_val=secn_nav)
    f_page.get_full_page_screenshot("Feature Page SS")
    feature_df = dfs['Features'].ffill() # type: ignore
    # # Feature
    # Module	Feature Info List	Feature Type	Feature Name	Feature URL
    # # Feature Controller Mapping
    # Module	Feature	Action	Parent Controller	Controllers
    # # Voucher Map
    # Project	Module	Event Type	Event	Amount Type	    Reference	Voucher Type	Dr Account Head Type	Dr Account Head	    Cr Account Head Type	Cr Account Head	    Remarks
    data_list = feature_df.to_dict(orient='records')
    for dt in data_list:
        f_page.perform_action(feat_name=dt['Module'], itm_name=dt['Feature Info List'])
        f_page.get_full_page_screenshot(f"Feature Selection {dt['Feature Name']} SS")
        
        
        feature_data = [dt['Feature Name'], dt['Feature URL']]
        fi_page.perform_action_2(feature_data = feature_data)
        
        
        secn_nav = ['Menu','Feature','Feature Controller Mapping']
        fcm_page.navigate_to_page(main_nav_val=main_nav, sub_nav_val=secn_nav)
        fcm_page.perform_action(data=dt)
    dt = {
        'module':'Microfinance',
        'feature':'VO',
        'action':'Garbage32',
        'feature_url':'loanAccount/getGroupInfoList',
        'controller':'VOCategoryController',
        'ctrl_item':'save'        
    }
    f_page.perform_action(dt['module'], dt['feature'])
    f_page.get_full_page_screenshot("Feature Selection SS")
    
    fi_page = feature_info_page(page)
    feature_data = [dt['action'], dt['feature_url']]
    fi_page.perform_action_2(feature_data = feature_data)
    
    fcm_page = feature_controller_mapping_page(page)    
    secn_nav = ['Menu','Feature','Feature Controller Mapping']
    fcm_page.navigate_to_page(main_nav_val=main_nav, sub_nav_val=secn_nav)
    fcm_page.perform_action(data=dt)

    ###################################################################################################################################
    ###################################################################################################################################
    
    uac_page = user_access_control_page(page)
    secn_nav = ['User','Access Control','Access Control']
    uac_page.navigate_to_page(main_nav_val=main_nav, sub_nav_val=secn_nav)
    uac_page.get_full_page_screenshot("User Access Control SS")
    dt2 = {
        'role':'ROLE_BA',
        'module':'Microfinance',
        'feature':'VO',
        'actions':{'Garbage32'},        
    }
    uac_page.set_user_access_for_feature_action(role=dt2['role'], module=dt2['module'], feature=dt2['feature'], actions=dt2['actions'])
    uac_page.get_full_page_screenshot("User Access Control Mapped SS")

    up_page = utility_page(page=page, base_url=test_url)
    up_page.perform_utility_action()


def test_03_perform_voucher_mapping(page):    
    main_nav = 'Accounting'
    secn_nav = ['Admin','Feature configuration','Chart of Accounts Mapping']
    vm_page = voucher_mapping_page(page)
    vm_page.navigate_to_page(main_nav_val=main_nav, sub_nav_val=secn_nav)
    vm_page.get_full_page_screenshot("Voucher Mapping Page SS")    
    
    coa_search_dt = {
        'project':'015 - Microfinance (Dabi)',
        'module':'Microfinance',
        'event_type':'Savings',
        'event':'Current Savings Collection',        
    }
    coa_map_dt = [    
        {
            'amount_type':'Current Savings Collection',
            'reference':'Voluntary Savings',
            'voucher_type':'Journal Voucher',
            'debit_head':'2104010101-01 - Current Accounts Deposit',
            'credit_head':'2104010101-01 - Current Accounts Deposit'
        },
        {
            'amount_type':'Balance Transfer In Own Branch For Other Project',
            'reference':'Voluntary Savings',
            'voucher_type':'Journal Voucher',
            'debit_head':'2104010101-01 - Current Accounts Deposit',
            'credit_head':'2110010101-08 - Current account with Head office'
        },
    ]
    vm_page.perform_action(coa_search_data=coa_search_dt, coa_map_data=coa_map_dt)


def test_99_logout_from_environment(page):
    f_page = feature_list_page(page)
    f_page.perform_logout()
    f_page.get_full_page_screenshot("Logout SS")