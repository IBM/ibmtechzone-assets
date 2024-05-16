package web_saucedemo.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import web_saucedemo.config.EnvironmentVariables;
import web_saucedemo.enums.AppMenu;

import java.time.Duration;

public class HeaderPage extends BasePage {

    By btnMenu = By.id("react-burger-menu-btn");
    By navMenu = By.xpath("//nav[contains(@class, 'bm-item-list')]/a[contains(@class,'bm-item')]");
    By lblCart = By.id("shopping_cart_container");

    public HeaderPage(WebDriver driver) {
        super(driver);
    }

    public HeaderPage navigateToMenu(AppMenu menu) {
        driver.findElement(btnMenu).click();

        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(EnvironmentVariables.WAIT_MAX));
        wait.until(ExpectedConditions.elementToBeClickable(navMenu));

        WebElement btnMenu = driver.findElements(navMenu)
                .stream()
                .filter(element -> element.getText().equalsIgnoreCase(menu.value()))
                .findFirst()
                .orElseThrow();
        btnMenu.click();
        return this;
    }

    public int getCartCount() {
        String count = driver.findElement(lblCart).getText();
        return count.isEmpty() ? 0: Integer.parseInt(count);
    }
}
