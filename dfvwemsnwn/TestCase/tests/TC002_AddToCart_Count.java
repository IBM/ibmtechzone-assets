package web_saucedemo.tests.testng.testcases;

import org.testng.Assert;
import org.testng.annotations.Test;
import web_saucedemo.enums.AppMenu;
import web_saucedemo.pages.HeaderPage;
import web_saucedemo.pages.LoginPage;
import web_saucedemo.pages.ProductsPage;

public class TC002_AddToCart_Count extends BaseTest {

    // TODO: Data provider
    String dtUsername = "standard_user";
    String dtPassword = "secret_sauce";

    String prod1 = "Sauce Labs Onesie";

    @Test
    private void test() {
        new LoginPage(driver).login(dtUsername, dtPassword);
        new HeaderPage(driver).navigateToMenu(AppMenu.LOGOUT);
    }

    @Test
    public void TC002_AddToCart_Count() {
        new LoginPage(driver).login(dtUsername, dtPassword);

        ProductsPage pgProducts = new ProductsPage(driver);
        pgProducts.add(prod1);

        HeaderPage pgHeader = new HeaderPage(driver);
        Assert.assertEquals(1, pgHeader.getCartCount());
    }
}
