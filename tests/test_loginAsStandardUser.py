from Pages.LoginPage import LoginPage


def test_verify_login_as_standard_user(navigate_to_saucedemo):
    driver = navigate_to_saucedemo
    login_page = LoginPage(driver)
    login_page.login_as_standard_user("standard_user", "secret_sauce")
    assert login_page.get_inventory_page_title() == "Products"

def test_verify_login_as_Locked_out_user(navigate_to_saucedemo):
    driver = navigate_to_saucedemo
    login_page = LoginPage(driver)
    login_page.login_as_lockedout_user("locked_out_user","secret_sauce")
    assert login_page.get_lockedoutuservalidation() == "Epic sadface: Sorry, this user has been locked out."