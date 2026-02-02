from Pages.Basepage import WebActions


class LoginPage(WebActions):
    
    def __init__(self, driver):
        super().__init__(driver)
        
    def mainloginsteps(self,username,password):
        self.type("LoginPageUsernameinputField_XPATH", username)
        self.type("LoginPagePasswordinputField_XPATH", password)
        self.click("LoginPageloginButton_XPATH")
        
        
        
    def login_as_standard_user(self):
        self.mainloginsteps("standard_user","secret_sauce")

    def get_inventory_page_title(self):
        return self._get_element("InventoryPageTitle_XPATH").text
        
        
    def login_as_lockedout_user(self):
        self.mainloginsteps("locked_out_user","secret_sauce")
        
        
        
    def get_lockedoutuservalidation(self):
        return self._get_element("lockedoutuservalidation_XPATH").text