from playwright.sync_api import sync_playwright, expect
from basic_actions import BasicActions

class user_access_control_page(BasicActions):
    def __init__(self, page):
        super().__init__(page)
        self.page = page       

        
    def set_user_access_for_feature_action(self, role, module, feature, action):
        try:
            # Select Role, Module, Feature and Action
            self.page.locator('#roleList').select_option(label=role)
            self.wait_for_timeout(500)
            self.page.locator('#moduleList').select_option(label=module)        
            # self.wait_for_timeout(500)
            # self.page.locator(f'//table[@id="request-map-table"]/tbody/tr/td/input[@value="{feature}"]')
            # for action in actions:
            self.wait_for_timeout(500)
            print(f'Clicking on {action}')
            self.page.locator(f'//table[@id="request-map-table"]/tbody/tr/td/input[@value="{feature}"]/parent::td/following-sibling::td/input[@value="{action}"]').click()
            self.wait_for_timeout(500)
            self.get_full_page_screenshot('Mapping Done')
            self.wait_for_timeout(2000)
            # Click Save Button
            self.page.locator('//input[@type="button" and @value="Save"]').click()
            self.page.wait_for_load_state('domcontentloaded')
        except Exception as e:
            print(f'Error in setting user access for feature action: {e}')

