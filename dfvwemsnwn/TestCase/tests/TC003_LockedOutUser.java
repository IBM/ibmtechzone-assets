package web_saucedemo.tests.testng.testcases;

import org.testng.Assert;
import org.testng.annotations.Test;
import web_saucedemo.pages.LoginPage;

public class TC003_LockedOutUser extends BaseTest {

    // TODO: Data provider
    String dtUsername = "locked_out_user";
    String dtPassword = "secret_sauce";

    @Test
    public void TC002_LockedOutUser() {
        LoginPage pgLogin = new LoginPage(driver);
        pgLogin.login(dtUsername, dtPassword);
        Assert.assertTrue(pgLogin.isUserLockedOut());
    }
}
