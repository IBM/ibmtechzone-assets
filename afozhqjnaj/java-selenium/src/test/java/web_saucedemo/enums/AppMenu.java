package web_saucedemo.enums;

public enum AppMenu {

    ALL_ITEMS ("All Items"),
    ABOUT ("About"),
    LOGOUT ("Logout"),
    RESET_APP_STATE ("Reset App State");

    private String menu;

    AppMenu(String menu) {
        this.menu = menu;
    }

    public String value() {
        return menu;
    }
}
