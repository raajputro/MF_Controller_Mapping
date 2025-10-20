from playwright.sync_api import sync_playwright, expect
from basic_actions import BasicActions

class feature_info_page(BasicActions):
    def __init__(self, page):
        super().__init__(page)
        page = self.page

        self.loc_edit_btn = page.locator('//input[@name="edit"]') # page.get_by_role('input', name='edit')
        self.loc_add_action_btn = page.locator('//input[@value="Add Action"]')
        self.loc_feat_action_table = page.locator('//div[@id="feature-action-table"]/div')


    def perform_action(self):
        try:        
            self.loc_edit_btn.click()
            self.get_full_page_screenshot("feature_info_edit")
            self.wait_to_load_element(self.loc_add_action_btn)
            action_count = self.loc_feat_action_table.count()
            print(f"Total Action Count 1: {action_count}")
            self.loc_add_action_btn.click()
            self.wait_for_timeout(2000)
            feature_data = ["Garbage8", "loanAccount/getGroupInfoList"]
            
            #ActionName                        
            self.page.locator(f'//input[@name="items.featureAction[{action_count}].actionName"]').fill(feature_data[0]) #1
            
            #Description            
            self.page.locator(f'//input[@name="items.featureAction[{action_count}].description"]').fill(feature_data[0]) #2
            
            #URL            
            self.page.locator(f'#showMenuUrls_{action_count}_item_input').click() #3.1
            self.page.locator(f'#showMenuUrls_{action_count}_item_input').fill(feature_data[1])
            # self.wait_for_timeout(500)            
            # self.page.locator(f'#showMenuUrls_{action_count}_item_arrow').click()
            self.wait_for_timeout(500)
            # self.page.locator(f'//span[@class="ffb-match" and contains(text(), "{feature_data[1]}")]').click(force=True)
            self.page.locator(f'//span[@class="row ffb-sel" and contains(text(),  "{feature_data[1]}")]').click(force=True)
            # if expect(self.page.locator(f'//span[text()="{feature_data[1]}"]')).to_be_visible():
                # print(f'Locator found!')
                # self.wait_for_timeout(500)
            # else:
            # self.page.locator(f'(//span[@id="showMenuUrls_{action_count}_item_arrow"])[1]/following-sibling::div/div/div[@val="{feature_data[1]}"').click()
            # self.page.wait_for_selector(f'//div[@name="items.featureAction[{action_count}].showMenuUrls"]/input[2]/following-sibling::div/div/div/div/span[text()="{feature_data[1]}"]').click()
                # self.page.wait_for_locator(f'//span[text()="{feature_data[1]}"]').click(force=True)            
            self.wait_for_timeout(2000)
            
            action_count = self.loc_feat_action_table.count()
            print(f"Total Action Count 2: {action_count}")
            self.get_full_page_screenshot("Action Added")
            
            self.page.locator('//*[@id="feature-info-form"]/div/div[3]/input').click()
            self.wait_for_timeout(2000)
            self.get_full_page_screenshot("Action Saved")

        except Exception as e:
            print(f"Got exception: {e}")


    def perform_action_2(self, feature_data):
            try:        
                self.loc_edit_btn.click()
                self.get_full_page_screenshot("feature_info_edit")
                self.wait_to_load_element(self.loc_add_action_btn)
                action_count = self.loc_feat_action_table.count()
                print(f"Total Action Count 1: {action_count}")
                self.loc_add_action_btn.click()
                self.wait_for_timeout(2000)                
                
                #ActionName                        
                self.page.locator(f'//input[@name="items.featureAction[{action_count}].actionName"]').fill(feature_data[0]) #1
                
                #Description            
                self.page.locator(f'//input[@name="items.featureAction[{action_count}].description"]').fill(feature_data[0]) #2
                
                #URL            
                self.page.locator(f'//input[@id="showMenuUrls_{action_count}_item_input"]').fill(feature_data[1])
                self.page.keyboard.press('Space')
                self.wait_for_timeout(1000)                
                self.page.locator(f'//div[@id="showMenuUrls_{action_count}_item_ctr"]/descendant::div[@val="{feature_data[1]}"]').click(force=True)
                self.wait_for_timeout(1000)
                
                # Checking count
                action_count = self.loc_feat_action_table.count()
                print(f"Total Action Count 2: {action_count}")
                self.get_full_page_screenshot("Action Added")
                
                self.page.locator('//*[@id="feature-info-form"]/div/div[3]/input').click()
                self.wait_for_timeout(2000)
                self.get_full_page_screenshot("Action Saved")

            except Exception as e:
                print(f"Got exception: {e}")
