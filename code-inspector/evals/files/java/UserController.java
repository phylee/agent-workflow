package evals.files.java;

import java.util.List;

public class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    public List<UserDto> listActiveUsers() {
        return userService.listActiveUsersWithOrders();
    }
}
