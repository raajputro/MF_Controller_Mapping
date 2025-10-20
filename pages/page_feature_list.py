from playwright.sync_api import sync_playwright
from basic_actions import BasicActions

class feature_list_page(BasicActions):
    def __init__(self, page):
        super().__init__(page)
        self.page = page
        # Elements to interact
        self.loc_feature_list = page.locator('select#listModuleList')


    def select_from_feature_list(self, featureName):
        self.loc_feature_list.select_option(label=featureName)

    def select_from_feature_info_list(self, itemName):
        fil_item = self.page.locator(f'//table[@id="feature-List-Grid"]/tbody/tr/td[text()="{itemName}"]/span')
        fil_item.click()
        self.wait_for_timeout(2000)
        self.select_first_item_from_info_list(itemName=itemName)

    def select_first_item_from_info_list(self, itemName):
        fil_item = self.page.locator(f'//table[@id="feature-List-Grid"]/tbody/tr/td[text()="{itemName}"]/parent::tr/following-sibling::tr/td[@title="{itemName}"]/a[text()="{itemName}"]').first
        fil_item.click()

    # Runner
    def perform_action(self, feat_name, itm_name):
        self.select_from_feature_list(featureName=feat_name)
        self.select_from_feature_info_list(itemName=itm_name)