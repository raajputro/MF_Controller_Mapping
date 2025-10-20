from playwright.sync_api import sync_playwright, expect
from basic_actions import BasicActions

class feature_controller_mapping_page(BasicActions):
    def __init__(self, page):
        super().__init__(page)
        self.page = page
        # Elements to interact
        self.loc_module_list = page.locator('#moduleList')
        self.loc_feature_list = page.locator('#featureList')
        self.loc_action_list = page.locator('#actionList')

        self.loc_add_controller_btn = page.locator('//input[@type="button" and @value="Add Controller"]')
        self.loc_save_controller_btn = page.locator('//input[@type="button" and @value="Save"]')

        self.loc_controller_list = page.locator('#controllerList-0')
        self.loc_controller_search_box = page.locator('//select[@id="controller-list[0]"]/following-sibling::div/descendant::input')
        self.loc_controller_item_add_btns = page.locator('//select[@id="controller-list[0]"]/following-sibling::div/descendant::ul[@class="available connected-list"]/li[@style="display: list-item;"]/a')


    def set_module_feature_action_controller(self, module, feature, action, controller):
        # Setting Module, Feature and Action
        self.loc_module_list.select_option(label=module)
        self.wait_for_timeout(500)
        self.loc_feature_list.select_option(label=feature)
        self.wait_for_timeout(500)
        self.loc_action_list.select_option(label=action)
        self.wait_for_timeout(500)
        # Click on Add Controller button
        self.loc_add_controller_btn.click()
        self.wait_for_timeout(500)
        # Set Controller value
        self.loc_controller_list.select_option(label=controller)
        self.wait_for_timeout(500)
        

    def search_and_add_controllers(self, controller_item):
        # Input controller item to search box
        self.loc_controller_search_box.fill(controller_item)
        self.wait_for_timeout(500)
        self.page.keyboard.press('Enter')
        self.wait_for_timeout(500)
        count = self.loc_controller_item_add_btns.count()
        for _ in range(count):
            # Add all controllers one-by-one
            self.loc_controller_item_add_btns.locator("nth=0").click()
            self.wait_for_timeout(500)
        # Save the map
        self.loc_save_controller_btn.click()
        self.wait_for_timeout(500)


    def perform_action(self, data):
        self.set_module_feature_action_controller(module=data['module'],feature=data['feature'],action=data['action'],controller=data['controller'])
        self.search_and_add_controllers(controller_item=data['ctrl_item'])