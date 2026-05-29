package evals.files.java;

import java.util.ArrayList;
import java.util.List;

public class UserService {
    private final UserRepository userRepository;
    private final OrderRepository orderRepository;

    public UserService(UserRepository userRepository, OrderRepository orderRepository) {
        this.userRepository = userRepository;
        this.orderRepository = orderRepository;
    }

    public List<UserDto> listActiveUsersWithOrders() {
        List<User> users = userRepository.findActiveUsers();
        List<UserDto> result = new ArrayList<>();

        for (User user : users) {
            List<Order> orders = orderRepository.findByUserId(user.getId());
            result.add(new UserDto(user.getId(), user.getEmail(), orders.size()));
        }

        return result;
    }
}
