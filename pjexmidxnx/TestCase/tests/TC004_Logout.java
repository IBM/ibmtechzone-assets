package web_saucedemo.tests.testng.testcases;

import org.testng.Assert;
import org.testng.annotations.Test;
import web_saucedemo.enums.AppMenu;
import web_saucedemo.pages.HeaderPage;
import web_saucedemo.pages.LoginPage;

public class TC004_Logout extends BaseTest {

    // TODO: Data provider
    String dtUsername = "standard_user";
    String dtPassword = "secret_sauce";

    @Test
    public void TC004_Logout() {
        LoginPage pgLogin = new LoginPage(driver);
        pgLogin.login(dtUsername, dtPassword);

        new HeaderPage(driver).navigateToMenu(AppMenu.LOGOUT);
        Assert.assertTrue(pgLogin.isAt());
    }
}
