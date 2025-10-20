from playwright.sync_api import sync_playwright, expect
from basic_actions import BasicActions

class voucher_mapping_page(BasicActions):
    def __init__(self, page):
        super().__init__(page)
        page = self.page

        # COA Mapping Page Elements : Project, Module, Event Type, Event
        self.loc_coa_map_search_by_label_dropdown = lambda label: page.locator(f'//label[contains(text(), "{label}")]//following-sibling::div//child::b')
        self.loc_coa_map_search_by_label_dropdown_input = lambda label: page.locator(f'//label[contains(text(), "{label}")]//following-sibling::select')
        self.loc_search_btn = page.locator('button.btn-sm')   

        # COA Mapping Table: Project = 1, Module = 2, Event Type = 3, Event = 4
        # This element is needed for filter value validation
        self.loc_table_column = lambda col: page.locator(f'//table[@id="eventCoaMappingGrid"]/tbody/tr/td[{col}]')

        self.loc_edit_btn = page.locator('a.red-stripe:nth-child(2)')
        self.loc_create_btn = page.locator('a.red-stripe:nth-child(1)')

        # element for amount type, reference, voucher type, debit head, credit head in the table
        # Amount Type = 2, Reference = 3, Voucher Type = 4
        self.loc_coa_details_dropdown = lambda col: page.locator(f'//tbody[@id="mappingDetailsTableBody"]/tr/td[{col}]/div')
        self.loc_coa_details_dropdown_input = lambda col: page.locator(f'//tbody[@id="mappingDetailsTableBody"]/tr/td[{col}]/select')
        # For Debit Head = 5, Credit Head = 6; Cash/Bank = 1, Other Account = 2
        self.loc_coa_details_acc_head_select = lambda col, type: page.locator(f'//tbody[@id="mappingDetailsTableBody"]/tr/td[{col}]/input[{type}]')
        self.loc_coa_details_acc_head_select_input = lambda col: page.locator(f'//tbody[@id="mappingDetailsTableBody"]/tr/td[{col}]/div/select')

        self.loc_coa_details_add_btn = page.locator('#add')
        self.loc_save_btn = page.locator('#save')

    def search_existing_coa_mapping(self, search_data):
        try:
            # select coa mapping search criteria
            for item in ['Project:','Module:','Event Type:','Event:']:
                self.loc_coa_map_search_by_label_dropdown(item).click()
                self.loc_coa_map_search_by_label_dropdown_input(item).select_option(label=search_data[item.lower().replace(' ','_').strip(':')])
                self.wait_for_timeout(500)
            # Click Search Button
            self.loc_search_btn.click()
            self.wait_for_timeout(2000)
            # Validate search results
            match = False
            for item, col in zip(['project','module','event_type','event'], [1,2,3,4]):
                all_values = self.loc_table_column(col).all_text_contents()
                if all(value == search_data[item] for value in all_values):
                    print(f"All values in column {col} match the search criteria: {search_data[item]}")
                    match = True
                else:
                    print(f"Some values in column {col} do not match the search criteria: {search_data[item]}")
            # Click on the first row to edit if match found
            if match:
                self.loc_table_column(1).click()
                self.loc_edit_btn.click()
                self.wait_for_timeout(2000)
        except Exception as e:
            print(f"Got exception: {e}")

    def perform_voucher_mapping(self, coa_map_data):
        try:
            for mapping in coa_map_data:
                self.loc_coa_details_dropdown(2).click()
                self.loc_coa_details_dropdown_input(2).select_option(label=mapping['amount_type'])
                self.wait_for_timeout(500)

                self.loc_coa_details_dropdown(3).click()
                self.loc_coa_details_dropdown_input(3).select_option(label=mapping['reference'])
                self.wait_for_timeout(500)

                self.loc_coa_details_dropdown(4).click()
                self.loc_coa_details_dropdown_input(4).select_option(label=mapping['voucher_type'])
                self.wait_for_timeout(500)

                self.loc_coa_details_acc_head_select(5,2).click()
                if self.loc_coa_details_acc_head_select_input(5).is_visible():
                    self.loc_coa_details_acc_head_select_input(5).select_option(label=mapping['debit_head'])
                    self.wait_for_timeout(500)

                self.loc_coa_details_acc_head_select(6,2).click()
                if self.loc_coa_details_acc_head_select_input(6).is_visible():
                    self.loc_coa_details_acc_head_select_input(6).select_option(label=mapping['credit_head'])
                    self.wait_for_timeout(500)

                self.loc_coa_details_add_btn.click()
                self.wait_for_timeout(1000)

            self.get_full_page_screenshot("Voucher Mapping Added")
            self.loc_save_btn.click()
            self.wait_for_timeout(2000)
            self.get_full_page_screenshot("Voucher Mapping Saved")

        except Exception as e:
            print(f"Got exception: {e}")

    def perform_action(self, coa_search_data, coa_map_data):
        self.search_existing_coa_mapping(search_data=coa_search_data)
        self.perform_voucher_mapping(coa_map_data=coa_map_data)



