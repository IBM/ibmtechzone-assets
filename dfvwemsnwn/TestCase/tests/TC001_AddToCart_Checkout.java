package web_saucedemo.tests.testng.testcases;

import org.testng.Assert;
import org.testng.annotations.Test;
import web_saucedemo.contexts.CheckoutYourInfoData;
import web_saucedemo.pages.CheckoutPage;
import web_saucedemo.pages.LoginPage;
import web_saucedemo.pages.ProductsPage;
import web_saucedemo.pages.ShoppingCartPage;

public class TC001_AddToCart_Checkout extends BaseTest {

    // TODO: Data provider
    String dtUsername = "standard_user";
    String dtPassword = "secret_sauce";

    String prod1 = "Sauce Labs Onesie";
    String prod2 = "Test.allTheThings() T-Shirt (Red)";

    @Test
    public void TC001_AddToCart_Checkout() {

        // TODO: Data provider
        CheckoutYourInfoData dtYourInfo = new CheckoutYourInfoData();
        dtYourInfo.setFirstName("John");
        dtYourInfo.setLastName("Doe");
        dtYourInfo.setZip("3000");

        new LoginPage(driver).login(dtUsername, dtPassword);
        new ProductsPage(driver)
                .add(prod1)
                .add(prod2);

        CheckoutPage pgCheckout = new ShoppingCartPage(driver)
                .open()
                .checkout()
                .setInformation(dtYourInfo)
                .finish();
        Assert.assertTrue(pgCheckout.isCheckoutComplete());
    }
}
